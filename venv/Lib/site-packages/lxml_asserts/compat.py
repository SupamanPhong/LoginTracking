# coding=utf-8

import sys

PY3 = sys.version_info[0] == 3

if PY3:
    exec("""
def raise_exc_info(exc_info):
    raise exc_info[1].with_traceback(exc_info[2])
""")
else:
    exec("""
def raise_exc_info(exc_info):
    raise exc_info[0], exc_info[1], exc_info[2]
""")

if PY3:
    unicode_type = str
else:
    unicode_type = unicode
