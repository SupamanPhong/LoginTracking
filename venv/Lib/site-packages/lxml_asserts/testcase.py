# coding=utf-8

import sys

from lxml_asserts import assert_xml_compatible, assert_xml_equal
from lxml_asserts.compat import raise_exc_info, unicode_type


class LxmlTestCaseMixin(object):
    """Mixin for L{unittest.TestCase}."""

    def assertXmlEqual(self, first, second, check_tags_order=False, msg=None):
        """
        Assert that two xml documents are equal.
        :param first: first etree object or xml string
        :param second: second etree object or xml string
        :param check_tags_order: if False, the order of children is ignored
        :param msg: custom error message
        :return: raises failureException if xml documents are not equal
        """
        if msg is None:
            msg = u'XML documents are not equal'

        try:
            assert_xml_equal(first, second, check_tags_order)
        except AssertionError as e:
            raise_exc_info((
                self.failureException, self.failureException(u'{} — {}'.format(msg, unicode_type(e))), sys.exc_info()[2]
            ))

    def assertXmlCompatible(self, first, second, msg=None):
        """
        Assert that second xml document is an extension of the first.
        (must contain all tags and attributes from the first xml and any number of extra tags and attributes).
        :param first: first etree object or xml string
        :param second: second etree object or xml string
        :param msg: custom error message
        :return: raises failureException if second xml document is not compatible with the first
        """
        if msg is None:
            msg = u'XML documents are not compatible'

        try:
            assert_xml_compatible(first, second)
        except AssertionError as e:
            raise_exc_info((
                self.failureException, self.failureException(u'{} — {}'.format(msg, unicode_type(e))), sys.exc_info()[2]
            ))
