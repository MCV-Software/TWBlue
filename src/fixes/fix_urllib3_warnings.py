# -*- coding: utf-8 -*-
from requests.packages import urllib3
from requests.packages.urllib3 import fields
import six

def fix():
 urllib3.disable_warnings()
 fields.format_header_param=patched_format_header_param

def patched_format_header_param(name, value):
    if not any(ch in value for ch in '"\\\r\n'):
        result = '%s="%s"' % (name, value)
        try:
            result.encode('ascii')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
        else:
            return result
    if not six.PY3 and isinstance(value, six.text_type):  # Python 2:
        value = value.encode('utf-8')
    value = '%s=%s' % (name, value)
    return value
