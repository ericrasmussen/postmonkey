import unittest

class TestPostMonkey(unittest.TestCase):
    def _makeOne(self, settings={}):
        from . import PostMonkey
        manager = PostMonkey(**settings)
        return manager

    def test_endpoint_from_settings(self):
        settings = {'endpoint': 'my_endpoint'}
        inst = self._makeOne(settings)
        self.assertEqual(inst.endpoint, 'my_endpoint')

    def test_endpoint_infer_datacenter(self):
        settings = {'apikey': 'fake_key-dc1'}
        inst = self._makeOne(settings)
        self.assertEqual(inst.endpoint,
                         'https://dc1.api.mailchimp.com/1.3/?method=')

    def test_endpoint_explicit_datacenter(self):
        settings = {'datacenter': 'my_dc'}
        inst = self._makeOne(settings)
        self.assertEqual(inst.endpoint,
                         'https://my_dc.api.mailchimp.com/1.3/?method=')

    def test_serialize_valid_payload(self):
        import json
        from urllib import unquote
        settings = {'default1':'', 'default2':''}
        inst = self._makeOne(settings)
        payload = {'param1':'', 'param2':''}
        serialized = unquote(inst._serialize_payload(payload))
        expected_dict = dict(default1='', default2='', param1='', param2='')
        deserialized_json = json.loads(serialized)
        self.assertEqual(deserialized_json, expected_dict)

    def test_serialize_invalid_payload(self):
        from .exceptions import SerializationError
        inst = self._makeOne()
        payload = { 'invalid_param': object() }
        self.assertRaises(SerializationError,
                          inst._serialize_payload, payload)

    def test_payload_takes_precedence(self):
        import json
        from urllib import unquote
        settings = {'default1':'', 'default2':''}
        inst = self._makeOne(settings)
        payload = {'default1':'overriden'}
        serialized = inst._serialize_payload(payload)
        deserialized = json.loads(unquote(serialized))
        self.assertEqual(deserialized['default1'], 'overriden')

    def test_deserialize_valid_response(self):
        import json
        sample = 'valid json'
        response = json.dumps(sample)
        inst = self._makeOne()
        deserialized = inst._deserialize_response(response)
        self.assertEqual(deserialized, sample)

    def test_deserialize_invalid_response(self):
        from .exceptions import DeserializationError
        inst = self._makeOne()
        response = '[[invalid json'
        self.assertRaises(DeserializationError,
                          inst._deserialize_response, response)

    def test_deserialize_bool_response(self):
        inst = self._makeOne()
        response = 'true'
        actual = inst._deserialize_response(response)
        self.assertEqual(actual, True)

    def test_deserialize_iterable_that_looks_like_an_error(self):
        import json
        inst = self._makeOne()
        sample = 'there was a code that led to an error'
        response = json.dumps(sample)
        deserialized = inst._deserialize_response(response)
        self.assertEqual(deserialized, sample)

    def test_method_call(self):
        inst = self._makeOne({'apikey': 'apikey'})
        inst.postrequest = dummy_post_request
        resp = inst.someMethodCall(param='my_param')
        received = resp['received']
        self.assertEqual(received['apikey'], 'apikey')
        self.assertEqual(received['param'], 'my_param')

    def test_method_call_post_fails(self):
        from .exceptions import PostRequestError
        inst = self._makeOne()
        def post_that_fails(*args, **kwargs):
            raise Exception
        inst.postrequest = post_that_fails
        self.assertRaises(PostRequestError, inst.someMethodCall)

    def test_method_call_mailchimp_exc(self):
        from .exceptions import MailChimpException
        inst = self._makeOne()
        inst.postrequest = dummy_post_exc
        self.assertRaises(MailChimpException, inst.someMethodCall)


class TestExceptions(unittest.TestCase):
    def test_SerializationError_captures_obj(self):
        from .exceptions import SerializationError
        dummy_obj = object()
        error = SerializationError(dummy_obj)
        self.assertEqual(error.obj, dummy_obj)
        self.assertIn(dummy_obj.__str__(), error.__str__())

    def test_DeserializationError_captures_obj(self):
        from .exceptions import DeserializationError
        dummy_obj = object()
        error = DeserializationError(dummy_obj)
        self.assertEqual(error.obj, dummy_obj)
        self.assertIn(dummy_obj.__str__(), error.__str__())

    def test_PostRequestError_captures_exc(self):
        from .exceptions import PostRequestError
        exc = Exception()
        caught = PostRequestError(exc)
        self.assertEqual(caught.exc, exc)
        self.assertIn(exc.__str__(), caught.__str__())

    def test_MailChimpException_attrs(self):
        from .exceptions import MailChimpException
        code = -90
        error = 'Method fake_method is not exported by this server'
        exc = MailChimpException(code, error)
        self.assertEqual(exc.code, code)
        self.assertEqual(exc.error, error)
        self.assertIn(error, exc.__str__())


class Test_postmonkey_from_settings(unittest.TestCase):
    def _makeOne(self, settings):
        from . import postmonkey_from_settings
        return postmonkey_from_settings(settings)

    def test_it(self):
        settings = {'postmonkey.apikey':'apikey', 'postmonkey.included': '',
                    'ignored':''}
        inst = self._makeOne(settings)
        self.assertEqual(inst.apikey, 'apikey')
        self.assertIn('included', inst.params)
        self.assertNotIn('ignored', inst.params)


class DummyResponse(object):
    def __init__(self, text):
        self.text = text

def dummy_post_request(url, data='', headers={}, timeout=None):
    import json
    from urllib import unquote
    params = json.loads(unquote(data))
    resp = {'received': params}
    json = json.dumps(resp)
    return DummyResponse(json)

def dummy_post_exc(*args, **kwargs):
    import json
    resp = {'code': 1, 'error': 'error'}
    json = json.dumps(resp)
    return DummyResponse(json)
