# coding: utf-8

import json
from tornado.escape import recursive_unicode, to_basestring

def json_encode(value, **kwargs):
    """JSON-encodes the given Python object."""
    # JSON permits but does not require forward slashes to be escaped.
    # This is useful when json data is emitted in a <script> tag
    # in HTML, as it prevents </script> tags from prematurely terminating
    # the javscript.  Some json libraries do this escaping by default,
    # although python's standard library does not, so we do it here.
    # http://stackoverflow.com/questions/1580647/json-why-are-forward-slashes-escaped
    return json.dumps(recursive_unicode(value), **kwargs).replace("</", "<\\/")


def json_decode(value, **kwargs):
    """Returns Python objects for the given JSON string."""
    return json.loads(to_basestring(value), **kwargs)
