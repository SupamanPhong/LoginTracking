# coding=utf-8

from collections import defaultdict

from lxml import etree
from lxml.doctestcompare import norm_whitespace

from lxml_asserts.graph_utils import find_max_matching


def _describe_element(elem):
    return elem.getroottree().getpath(elem)


def _xml_compare_text(t1, t2, strip):
    t1 = t1 or ''
    t2 = t2 or ''

    if strip:
        t1 = norm_whitespace(t1).strip()
        t2 = norm_whitespace(t2).strip()

    return t1 == t2


def _assert_tag_and_attributes_are_equal(xml1, xml2, can_extend=False):
    if xml1.tag != xml2.tag:
        raise AssertionError(u'Tags do not match: {tag1} != {tag2}'.format(
            tag1=_describe_element(xml1), tag2=_describe_element(xml2)
        ))

    added_attributes = set(xml2.attrib).difference(xml1.attrib)
    missing_attributes = set(xml1.attrib).difference(xml2.attrib)

    if missing_attributes:
        raise AssertionError(u'Second xml misses attributes: {path}/({attributes})'.format(
            path=_describe_element(xml2), attributes=','.join(missing_attributes)
        ))

    if not can_extend and added_attributes:
        raise AssertionError(u'Second xml has additional attributes: {path}/({attributes})'.format(
            path=_describe_element(xml2), attributes=','.join(added_attributes)
        ))

    for attrib in xml1.attrib:
        if not _xml_compare_text(xml1.attrib[attrib], xml2.attrib[attrib], False):
            raise AssertionError(u"Attribute values are not equal: {path}/{attribute}['{v1}' != '{v2}']".format(
                path=_describe_element(xml1), attribute=attrib, v1=xml1.attrib[attrib], v2=xml2.attrib[attrib]
            ))

    if not _xml_compare_text(xml1.text, xml2.text, True):
        raise AssertionError(u"Tags text differs: {path}['{t1}' != '{t2}']".format(
            path=_describe_element(xml1), t1=xml1.text, t2=xml2.text
        ))

    if not _xml_compare_text(xml1.tail, xml2.tail, True):
        raise AssertionError(u"Tags tail differs: {path}['{t1}' != '{t2}']".format(
            path=_describe_element(xml1), t1=xml1.tail, t2=xml2.tail
        ))


def _assert_xml_docs_are_equal(xml1, xml2, check_tags_order=False):
    _assert_tag_and_attributes_are_equal(xml1, xml2)

    children1 = list(xml1)
    children2 = list(xml2)

    if len(children1) != len(children2):
        raise AssertionError(u'Children are not equal: {path}[{len1} children != {len2} children]'.format(
            path=_describe_element(xml1), len1=len(children1), len2=len(children2)
        ))

    if check_tags_order:
        for c1, c2 in zip(children1, children2):
            _assert_xml_docs_are_equal(c1, c2, True)

    else:
        children1 = set(children1)
        children2 = set(children2)

        for c1 in children1:
            c1_match = None

            for c2 in children2:
                try:
                    _assert_xml_docs_are_equal(c1, c2, False)
                except AssertionError:
                    pass
                else:
                    c1_match = c2
                    break

            if c1_match is None:
                raise AssertionError(u'No equal child found in second xml: {path}'.format(path=_describe_element(c1)))

            children2.remove(c1_match)


def _assert_xml_docs_are_compatible(xml1, xml2):
    _assert_tag_and_attributes_are_equal(xml1, xml2, can_extend=True)

    children1 = list(xml1)
    children2 = list(xml2)

    if not children1:
        return

    elif len(children2) < len(children1):
        raise AssertionError(u'Second xml {path} contains less children ({len2} < {len1})'.format(
            path=_describe_element(xml1), len1=len(children1), len2=len(children2)
        ))

    else:
        compatibility_bipartite_graph = defaultdict(set)

        for c1 in children1:
            for c2 in children2:
                try:
                    _assert_xml_docs_are_compatible(c1, c2)
                except AssertionError:
                    pass
                else:
                    compatibility_bipartite_graph[c1].add(c2)

            if not compatibility_bipartite_graph[c1]:
                raise AssertionError(
                    u'Second xml has no compatible child for {path}'.format(path=_describe_element(c1))
                )

        max_matching = find_max_matching(compatibility_bipartite_graph)
        any_missing = next((c for c in children1 if c not in max_matching), None)

        if any_missing is not None:
            raise AssertionError(
                u'Second xml has no compatible child for {path}'.format(path=_describe_element(any_missing))
            )


def _assert_xml_compare(cmp_func, xml1, xml2, **kwargs):
    if not isinstance(xml1, etree._Element):
        xml1 = etree.fromstring(xml1)

    if not isinstance(xml2, etree._Element):
        xml2 = etree.fromstring(xml2)

    cmp_func(xml1, xml2, **kwargs)


def assert_xml_equal(first, second, check_tags_order=False):
    """
    Asserts that two xml documents are equal.
    :param first: first etree object or xml string
    :param second: second etree object or xml string
    :param check_tags_order: if False, the order of children is ignored
    :return: raises AssertionError if documents are not equal
    """
    _assert_xml_compare(_assert_xml_docs_are_equal, first, second, check_tags_order=check_tags_order)


def assert_xml_compatible(first, second):
    """
    Asserts that second xml document is an extension of the first.
    (must contain all tags and attributes from the first xml and any number of extra tags and attributes).
    :param first: first etree object or xml string
    :param second: second etree object or xml string
    :return: raises AssertionError if second xml document is not compatible
    """
    _assert_xml_compare(_assert_xml_docs_are_compatible, first, second)
