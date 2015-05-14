import unittest
from wiki2json import Wiki2Json
from io import StringIO
import sys


class TestWiki2Json(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TestWiki2Json._stdout_bak = sys.stdout

    @classmethod
    def tearDownClass(cls):
        sys.stdout = TestWiki2Json._stdout_bak

    def setUp(self):
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout.close()

    def test_header_tags(self):
        actual = self._parse("""
          <mediawiki xmlns="http://www.mediawiki.org">
  <siteinfo>
  <sitename>Wikipedia</sitename>
  </siteinfo>""")
        expected = ''
        self.assertEqual(expected, actual)

    def test_root_one_line_tag(self):
        actual = self._parse("""
  <page>
    <tag>some text</tag>
  </page>""")
        expected = '{"tag":"some text"}'
        self.assertEqual(expected, actual)

    def test_root_multiple_lines(self):
        actual = self._parse("""
  <page>
    <text  xml:space="preserve">1st line.
2nd line.
3rd line.</text>
 </page>""")
        expected = '{"text":"1st line. 2nd line. 3rd line."}'
        self.assertEqual(expected, actual)

    def test_multiple_one_lines(self):
        actual = self._parse("""
  <page>
    <tag1>text 1</tag1>
    <tag2>text 2</tag2>
  </page>""")
        expected = '{"tag1":"text 1","tag2":"text 2"}'
        self.assertEqual(expected, actual)

    def test_multiple_multiple_lines(self):
        actual = self._parse("""
  <page>
    <text1  xml:space="preserve">1 1.
1 2.
1 3.</text1>
    <text2  xml:space="preserve">2 1.
2 2.
2 3.</text2>
  </page>""")
        expected = '{"text1":"1 1. 1 2. 1 3."' \
                   ',"text2":"2 1. 2 2. 2 3."}'
        self.assertEqual(expected, actual)

    def test_mixed_one_line_multiple_lines(self):
        actual = self._parse("""
  <page>
    <text  xml:space="preserve">line 1.
line 2.
line 3.</text>
    <tag>some text</tag>
  </page>""")
        expected = '{"text":"line 1. line 2. line 3."' \
                   ',"tag":"some text"}'
        self.assertEqual(expected, actual)

    def test_2_level_tag(self):
        actual = self._parse("""
  <page>
    <out>
      <in>some text</in>
    </out>
  </page>""")
        expected = '{"out":{"in":"some text"}}'
        self.assertEqual(expected, actual)

    def test_2_level_multiple(self):
        actual = self._parse("""
  <page>
    <out>
      <in1>in 1</in1>
      <in2>in 2</in2>
    </out>
  </page>""")
        expected = '{"out":{"in1":"in 1","in2":"in 2"}}'
        self.assertEqual(expected, actual)

    def test_parent_sibling(self):
        actual = self._parse("""
  <page>
    <out1>
      <in1>in 1</in1>
    </out1>
    <out2>
      <in2>in 2</in2>
    </out2>
  </page>""")
        expected = '{"out1":{"in1":"in 1"},"out2":{"in2":"in 2"}}'
        self.assertEqual(expected, actual)

    def test_grandparent_sibling(self):
        actual = self._parse("""
  <page>
    <out1>
      <mid1>
        <in1>in 1</in1>
      </mid1>
    </out1>
    <out2>
      <in2>in 2</in2>
    </out2>
  </page>""")
        expected = '{"out1":{"mid1":{"in1":"in 1"}}' \
                   ',"out2":{"in2":"in 2"}}'
        self.assertEqual(expected, actual)

    def test_2_pages(self):
        actual = self._parse("""
  <page>
    <tag>First page</tag>
  </page>
  <page>
    <tag>Second page</tag>
  </page>""")
        expected = '{"tag":"First page"}\n' \
                   '{"tag":"Second page"}'
        self.assertEqual(expected, actual)

    def test_empty_tag_as_boolean(self):
        actual = self._parse("""
  <page>
    <redirect title="Computer accessibility" />
    <minor />
  </page>""")
        expected = '{"redirect":true,"minor":true}'
        self.assertEqual(expected, actual)

    def test_3_level_tag(self):
        actual = self._parse("""
  <page>
    <t1>
      <t2>
        <t3>some
text</t3>
      </t2>
    </t1>
  </page>""")
        expected = '{"t1":{"t2":{"t3":"some text"}}}'
        self.assertEqual(expected, actual)

    def test_escaping(self):
        actual = self._parse("""
  <page>
    <escapeme>\ "</escapeme>
  </page>""")
        expected = r'{"escapeme":"\\ \""}'
        self.assertEqual(expected, actual)

    def test_timestamp_conversion(self):
        actual = self._parse("""
  <page>
    <timestamp>2015-03-04T13:45:11Z</timestamp>
  </page>""")
        expected = '{"timestamp":1425476711}'
        self.assertEqual(expected, actual)

    def test_numeric_tags(self):
        actual = self._parse("""
  <page>
    <ns>0</ns>
    <id>1</id>
    <parentid>42</parentid>
  </page>""")
        expected = '{"ns":0,"id":1,"parentid":42}'
        self.assertEqual(expected, actual)

    def test_tag_trailing_spaces(self):
        actual = self._parse("""
  <page> 
    <revision> 
      <text xml:space="preserve"> 
1 1.
      </text> 
      <sha1>hash</sha1> 
    </revision> 
  </page>  """)
        expected = '{"revision":{"text":"1 1. ","sha1":"hash"}}'
        self.assertEqual(expected, actual)

    def test_deleted_contributor_should_be_null(self):
        actual = self._parse("""
  <page>
    <revision>
      <contributor deleted="deleted" />
        <text>Test</text>
      </revision>
    </page>""")
        expected = '{"revision":{"text":"Test"}}'
        self.assertEqual(expected, actual)

    def test_no_newlines_between_jsons(self):
        actual = self._parse("""
  <page>
    <tag>Test</tag>
  </page>
  <page>
    <tag>Test</tag>
  </page>""")
        expected = '{"tag":"Test"}\n{"tag":"Test"}'
        self.assertEqual(expected, actual)

    def _parse(self, xml):
        w2j = Wiki2Json()
        for line in xml.split('\n'):
            w2j.parse_line(line + '\n')
        return sys.stdout.getvalue()[:-1]


if __name__ == '__main__':
    unittest.main()
