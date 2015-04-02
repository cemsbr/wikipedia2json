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
        actual = self._parse([
            '<mediawiki xmlns="http://www.mediawiki.org">\n',
            '  <siteinfo>\n',
            '  <sitename>Wikipedia</sitename>\n',
            '  </siteinfo>\n'])
        expected = ''
        self.assertEqual(expected, actual)

    def test_root_one_line_tag(self):
        actual = self._parse([
            '  <page>\n',
            '    <tag>some text</tag>\n',
            '  </page>\n'])
        expected = '{"tag":"some text"}'
        self.assertEqual(expected, actual)

    def test_root_multiple_lines(self):
        actual = self._parse([
            '  <page>\n',
            '    <text  xml:space="preserve">1st line.\n',
            '2nd line.\n',
            '3rd line.</text>\n',
            ' </page>\n'])
        expected = '{"text":"1st line. 2nd line. 3rd line."}'
        self.assertEqual(expected, actual)

    def test_multiple_one_lines(self):
        actual = self._parse([
            '  <page>\n',
            '    <tag1>text 1</tag1>\n',
            '    <tag2>text 2</tag2>\n',
            '  </page>\n'])
        expected = '{"tag1":"text 1","tag2":"text 2"}'
        self.assertEqual(expected, actual)

    def test_multiple_multiple_lines(self):
        actual = self._parse([
            '  <page>\n',
            '    <text1  xml:space="preserve">1 1.\n',
            '1 2.\n',
            '1 3.</text1>\n',
            '    <text2  xml:space="preserve">2 1.\n',
            '2 2.\n',
            '2 3.</text2>\n',
            '  </page>\n'])
        expected = '{"text1":"1 1. 1 2. 1 3."' \
                   ',"text2":"2 1. 2 2. 2 3."}'
        self.assertEqual(expected, actual)

    def test_mixed_one_line_multiple_lines(self):
        actual = self._parse([
            '  <page>\n',
            '    <text  xml:space="preserve">line 1.\n',
            'line 2.\n',
            'line 3.</text>\n',
            '    <tag>some text</tag>\n',
            '  </page>\n'])
        expected = '{"text":"line 1. line 2. line 3."' \
                   ',"tag":"some text"}'
        self.assertEqual(expected, actual)

    def test_2_level_tag(self):
        actual = self._parse([
            '  <page>\n',
            '    <out>\n',
            '      <in>some text</in>\n',
            '    </out>\n',
            '  </page>\n'])
        expected = '{"out":{"in":"some text"}}'
        self.assertEqual(expected, actual)

    def test_2_level_multiple(self):
        actual = self._parse([
            '  <page>\n',
            '    <out>\n',
            '      <in1>in 1</in1>\n',
            '      <in2>in 2</in2>\n',
            '    </out>\n',
            '  </page>\n'])
        expected = '{"out":{"in1":"in 1","in2":"in 2"}}'
        self.assertEqual(expected, actual)

    def test_parent_sibling(self):
        actual = self._parse([
            '  <page>\n',
            '    <out1>\n',
            '      <in1>in 1</in1>\n',
            '    </out1>\n',
            '    <out2>\n',
            '      <in2>in 2</in2>\n',
            '    </out2>\n',
            '  </page>\n'])
        expected = '{"out1":{"in1":"in 1"},"out2":{"in2":"in 2"}}'
        self.assertEqual(expected, actual)

    def test_grandparent_sibling(self):
        actual = self._parse([
            '  <page>\n',
            '    <out1>\n',
            '      <mid1>\n',
            '        <in1>in 1</in1>\n',
            '      </mid1>\n',
            '    </out1>\n',
            '    <out2>\n',
            '      <in2>in 2</in2>\n',
            '    </out2>\n',
            '  </page>\n'])
        expected = '{"out1":{"mid1":{"in1":"in 1"}}' \
                   ',"out2":{"in2":"in 2"}}'
        self.assertEqual(expected, actual)

    def test_2_pages(self):
        actual = self._parse([
            '  <page>\n',
            '    <tag>First page</tag>\n',
            '  </page>\n',
            '  <page>\n',
            '    <tag>Second page</tag>\n',
            '  </page>\n'])
        expected = '{"tag":"First page"}\n' \
                   '{"tag":"Second page"}'
        self.assertEqual(expected, actual)

    def test_empty_tag_as_boolean(self):
        actual = self._parse([
            '  <page>\n',
            '    <redirect title="Computer accessibility" />\n',
            '    <minor />\n',
            '  </page>\n'])
        expected = '{"redirect":true,"minor":true}'
        self.assertEqual(expected, actual)

    def test_3_level_tag(self):
        actual = self._parse([
            '  <page>\n',
            '    <t1>\n',
            '      <t2>\n',
            '        <t3>some\n',
            'text</t3>\n',
            '      </t2>\n',
            '    </t1>\n',
            '  </page>\n'])
        expected = '{"t1":{"t2":{"t3":"some text"}}}'
        self.assertEqual(expected, actual)

    def test_escaping(self):
        actual = self._parse([
            '  <page>\n',
            '    <escapeme>\ "</escapeme>\n',
            '  </page>\n'])
        expected = r'{"escapeme":"\\ \""}'
        self.assertEqual(expected, actual)

    def test_timestamp_conversion(self):
        actual = self._parse([
            '  <page>\n',
            '    <timestamp>2015-03-04T13:45:11Z</timestamp>\n',
            '  </page>'])
        expected = '{"timestamp":1425444311}'
        self.assertEqual(expected, actual)

    def test_numeric_tags(self):
        actual = self._parse([
            '  <page>\n',
            '    <ns>0</ns>\n',
            '    <id>1</id>\n',
            '    <parentid>42</parentid>\n',
            '  </page>'])
        expected = '{"ns":0,"id":1,"parentid":42}'
        self.assertEqual(expected, actual)

    def _parse(self, lines):
        w2j = Wiki2Json()
        for line in lines:
            w2j.parse_line(line)
        return sys.stdout.getvalue()[:-1]


if __name__ == '__main__':
    unittest.main()
