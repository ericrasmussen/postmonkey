Reading MailChimp's API
=======================


Parameters and Types
--------------------

So let's be honest: these `PostMonkey` docs are lazy. You will find examples,
but you won't find the complete API documented anywhere here. The main reason is
MailChimp's API docs should be the one source of truth. Ultimately, no matter
how much effort we put into keeping these docs up to date, they won't be a
substitute for reading the
`actual API docs <http://apidocs.mailchimp.com/api/1.3/>`_.

The problem is the actual API docs can be hard to read. Let's define some
terms and work through a few examples so you can understand how they correspond
to using `PostMonkey`.


A typical `PostMonkey` call looks like this:

.. code-block:: python

    postmonkey_instance.mailchimpMethodName(param_1=value_1,
                                            param_2=value_2,
                                            param_n=value_n)


The keyword arguments you supply to the method are automatically translated into
a javascript object in the form:

.. code-block:: javascript

    { 'param_1': value_1, 'param_2': value_2, 'param_3': value_3 }

Where each of the values is rendered into an appropriate JSON
representation by python's
`json module <http://docs.python.org/2/library/json.html>`_.

This is all pretty standard so far, but the catch is that MailChimp doesn't
document their API solely for JSON. The parameters they document use their own
internal types that are (relatively) neutral for the different formats they
support, but it's not always immediately obvious how they translate to json
and back to python.

Here's a pretty table that should help:

   +------------+---------------+
   | MailChimp  | Python        |
   +============+===============+
   | string     | string        |
   +------------+---------------+
   | int        | int           |
   +------------+---------------+
   | array      | dict or list  |
   +------------+---------------+
   | boolean    | bool          |
   +------------+---------------+

The only surprising one there is that when MailChimp documents a parameter as
an array, they might mean you need a dict and they might mean you need a list.
If the docs were only for JSON, we could hope they would distinguish between
objects and arrays. Instead, their arrays appear to be the same as PHP arrays,
which can mean one of two things for our purposes:

* an associative array mapping keys to values
* an indexed array of values (where the keys are implicit indices beginning at 0)

Let's look at a couple examples. Here are the documented parameters for the
`listSubscribe` method::

    listSubscribe(string apikey,
                  string id,
                  string email_address,
                  array merge_vars,
                  string email_type,
                  bool double_optin,
                  bool update_existing,
                  bool replace_interests,
                  bool send_welcome)

At first glance, the `merge_vars` parameter appears ambiguous now that we know
it could be represented in python as a dict or a list. However, if you view
the table with detailed descriptions on the
`documentation for listSubscribe <http://apidocs.mailchimp.com/api/1.3/listsubscribe.func.php>`_,
you'll see another listing of parameters and a description of fields that have
names. This indicates that you need to supply an *associative array*, meaning
a json object, meaning a python dict.

You can see an example in :ref:`merge_vars <merge-vars>`.

Now let's look at `listBatchUnsubscribe`::

    listBatchUnsubscribe(string apikey,
                         string id,
                         array emails,
                         boolean delete_member,
                         boolean send_goodbye,
                         boolean send_notify)

When you read the
`documentation for listBatchUnsubscribe <http://apidocs.mailchimp.com/api/1.3/listbatchunsubscribe.func.php>`_
and check the parameter descriptions, the "emails" parameter doesn't mention
anything about names or keys, only an "array of email addresses". This is our
clue that we can supply a python list like this:

.. code-block:: python

    postmonkey_instance.listBatchUnsubscribe(id='<your_list_id>',
                                             emails=['email_1', 'email_2'])



.. _merge-vars:

merge_vars in Depth
-------------------

MailChimp allows you to store extra fields on subscriber accounts so you can
personalize campaigns. The simplest example is having your campaign begin with:

`Hello, *|FNAME|*!`

Where `*|FNAME|*` will be replaced with the value of each user's FNAME merge
variable.

The MailChimp API docs declare these `merge_vars` to be of type "array", but
as we just discovered, that can mean different things depending on the context.
In this case, they are defineitely referring to an associative array, which
can be easily represented as a python dict.

Here's an example of calling `listSubscribe` with merge_vars:

.. code-block:: python

    pm.listSubscribe(id='<your_list_id>',
                     email_address='<subscriber_email>',
                     merge_vars={'FNAME': 'Mail', 'LNAME': 'Chimp'})


