"""Tests for the :func:`~polymatheia.data.xml_to_navigable_dict` function."""
from lxml import etree

from polymatheia.data import xml_to_navigable_dict


def test_simple_xml():
    """Test basic parsing of XML."""
    tree = xml_to_navigable_dict(etree.fromstring('<test><element>Test</element></test>'))
    assert '_text' not in tree
    assert '_tail' not in tree
    assert '_attrib' not in tree
    assert tree.element._text == 'Test'
    assert '_tail' not in tree.element
    assert '_attrib' not in tree.element


def test_tail_xml():
    """Test the text and tail appear where expected."""
    tree = xml_to_navigable_dict(etree.fromstring('<test><element>Test</element> this</test>'))
    assert '_text' not in tree
    assert '_tail' not in tree
    assert tree.element._text == 'Test'
    assert tree.element._tail == ' this'


def test_list_xml():
    """Test that where elements occur multiple times, a list is generated."""
    tree = xml_to_navigable_dict(etree.fromstring('<test><element>Test</element><element>Test 2</element></test>'))
    assert isinstance(tree.element, list)
    assert len(tree.element) == 2
    assert tree.element[0]._text == 'Test'
    assert tree.element[1]._text == 'Test 2'


def test_mixed_xml():
    """Test that mixed XML is correctly parsed."""
    tree = xml_to_navigable_dict(etree.fromstring('<test>Hello <name>World</name>!</test>'))
    assert tree._text == 'Hello '
    assert tree.name._text == 'World'
    assert tree.name._tail == '!'


def test_attributed_xml():
    """Test that attributes are correctly parsed."""
    tree = xml_to_navigable_dict(etree.fromstring('<test><element id="first">Test</element></test>'))
    assert tree.element._text == 'Test'
    assert tree.element._attrib.id == 'first'


def test_namespaced_xml():
    """Test that namespaced XML is correctly parsed and the namespaces mapped."""
    tree = xml_to_navigable_dict(etree.fromstring(
        '<a:test xmlns:a="http://example.com/a" xmlns:b="http://example.com/b">' +
        '<b:element b:id="test">Test</b:element></a:test>'))
    assert tree.b_element._text == 'Test'
    assert tree.b_element._attrib.b_id == 'test'


def test_default_namespace_xml():
    """Test that the default namespace is stripped."""
    tree = xml_to_navigable_dict(etree.fromstring(
        '<test xmlns="http://example.com/b"><element id="test">Test</element></test>'))
    assert tree.element._text == 'Test'
    assert tree.element._attrib.id == 'test'
