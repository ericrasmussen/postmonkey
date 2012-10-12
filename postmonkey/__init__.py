import json
import requests
from urllib import quote
from functools import partial

from . exceptions import (
    SerializationError,
    DeserializationError,
    PostRequestError,
    MailChimpException,
    )


class PostMonkey(object):
    """ ``apikey``

          The API key for your MailChimp account, obtained from MailChimp.

        ``endpoint``

          The URL used for API calls. Will be inferred from your API key unless
          you specifically override it (not recommended except for testing).

        ``datacenter``

          The MailChimp supplied data center for your account. Will be inferred
          from your API key unless you specifically override it. Cannot be
          accessed or modified after initialization.

        ``params``

          Any extra keyword arguments supplied on initialization will be made
          available in a dict via this attribute. Only include parameters that
          should be used on each and every API call. For instance, if you
          want to add a subscription form to your website, you can parameterize
          the list's ID.

        ``postrequest``

          Defaults to ``requests.post``, and should not be changed except for
          testing or if you have a really good reason. If you do override it,
          you must supply a function that takes a URL, a JSON encoded payload,
          a dict of HTTP headers, and optionally a timeout (in seconds). Must
          return a response object with a ``text`` attribute containing valid
          JSON.

    """
    def __init__(self,
                 apikey='',
                 endpoint=None,
                 datacenter=None,
                 timeout=None,
                 **params):
        self.apikey = apikey
        self.params = params
        self.endpoint = endpoint or self._make_endpoint(datacenter)
        self.postrequest = partial(requests.post, timeout=timeout)

    def __getattr__(self, name):
        """ Returns a callable function that will make an HTTP request to
        ``self.endpoint`` using the supplied method ``name``.
        """
        method_call = partial(self._make_method_call, name)
        return method_call

    def _make_method_call(self, methodname, **kwargs):
        """ Make an API request to MailChimp using ``methodname``,
        ``self.apikey``, ``self.params``, and the supplied ``kwargs``.
        Attempts to deserialize the JSON response and return a python
        representation.

        Will raise ``SerializationError`` if supplied a method
        name or ``kwargs`` that cannot be serialized to JSON.

        Will raise ``PostRequestError`` if the POST transaction fails.

        Will raise ``DeserializationError`` if the response text is not
        valid JSON.

        Will raise ``MailChimpException`` if MailChimp returns an exception
        code.
        """
        url = self.endpoint + methodname
        headers = {'content-type': 'application/json'}
        kwargs['apikey'] = self.apikey
        payload = self._serialize_payload(kwargs)

        try:
            resp = self.postrequest(url, data=payload, headers=headers)
        except Exception, e:
            raise PostRequestError(e)

        decoded = self._deserialize_response(resp.text)
        return decoded

    def _make_endpoint(self, maybe_datacenter):
        """ Creates an endpoint URL using ``maybe_datacenter`` (if not None) or
        inferring the data center from the API key, which has a suffix in the
        form "-<your_data_center>".
        """
        base_url = 'https://%s.api.mailchimp.com/1.3/?method='
        datacenter = maybe_datacenter or self.apikey.split('-')[-1]
        return base_url % datacenter

    def _serialize_payload(self, payload):
        """ Merges any default parameters from ``self.params`` with the
        ``payload`` (giving the ``payload`` precedence) and attempts to
        serialize the resulting ``dict`` to JSON.
        Note: MailChimp expects the JSON string to be quoted (their docs
        call it "URL encoded", but python's ``urllib`` calls it "quote").

        Raises a ``SerializationError`` if data cannot be serialized.
        """
        params = self.params.copy()
        params.update(payload)
        try:
            jsonstr = json.dumps(params)
            serialized = quote(jsonstr)
            return serialized
        except TypeError:
            raise SerializationError(payload)

    def _deserialize_response(self, text):
        """ Attempt to deserialize a JSON response from the server."""
        try:
            deserialized = json.loads(text)
        except ValueError:
            raise DeserializationError(text)

        self._fail_if_mailchimp_exc(deserialized)

        return deserialized

    def _fail_if_mailchimp_exc(self, response):
        """ If MailChimp returns an exception code and error, raise
        ``MailChimpException``. This allows callers to wrap method calls in a
        try/except clause and work with a single exception type for any
        error returned by MailChimp.
        """
        # case: response is not a dict so it cannot be an error response
        if not isinstance(response, dict):
            return
        # case: response is a dict and may be an error response
        elif 'code' in response and 'error' in response:
            raise MailChimpException(response['code'], response['error'])

def postmonkey_from_settings(settings):
    """ Factory method that takes a dict, finds keys prefixed with
    'postmonkey.', and uses them to create a new ``PostMonkey`` instance.
    Intended for use with console scripts or web frameworks that load config
    file data into a dict.
    """
    pm_keys = filter(lambda k: k.startswith('postmonkey.'), settings)
    pm_opts = {}
    for key in pm_keys:
        param = key.split('.')[-1]
        value = settings[key]
        pm_opts[param] = value
    return PostMonkey(**pm_opts)
