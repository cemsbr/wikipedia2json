import re
import sys


class Node:
    def __init__(self):
        self.has_value = False
        self.terminator = None

    @property
    def separator(self):
        if self.has_value:
            return ','
        else:
            self.terminator = '}'
            return '{'


class Wiki2Json:
    def __init__(self):
        # One-line key-value
        self._re_one_line = re.compile(r'^\s+<(\w+).*?>(.+)</\1>\s*$')
        # Beginning of a tag and maybe the beginning of its text
        self._re_beg_tag = re.compile(r'^\s+<([^/]\w+).*?>(.*\S.*)?$')
        # Tag-end regexes will be dynamically generated
        self._re_end_tags = []
        # Only parses 'page' tags
        self._re_beg_page = re.compile(r'^\s+<page>\s*$')
        self._re_end_page = re.compile(r'^\s+</page>\s*$')
        self._re_empty = re.compile('^\s+<\w+.*/>')
        self._reset()

    def _reset(self):
        del self._re_end_tags[:]
        # To keep track of separators and endings
        self._parents = [Node()]  # root parent
        self._in_page = False

    def parse_line(self, line):
        # <page>
        if not self._in_page:
            if self._re_beg_page.match(line):
                self._in_page = True
        # </page>
        elif self._re_end_page.match(line):
            self._in_page = False
            print('}')
            self._reset()
        # between <page> and </page>
        elif not self._re_empty.match(line):
            self._parse_page(line)

    def _parse_page(self, line):
        m = self._re_one_line.match(line)
        if m is not None:
            # <tag>text</tag>
            self._append_separator()
            print('"%s":"%s"' % (m.group(1), m.group(2)), end='')
            self._parent().has_value = True
        elif not self._re_empty.match(line):
            self._parse_multiline_tag(line)

    def _parse_multiline_tag(self, line):
        m = self._re_beg_tag.match(line)
        if m is not None:
            # <tag>...
            self._init_multiline_tag(m.group(1))
            if not m.group(2) is None:
                self._append_text('"%s ' % m.group(2))
                self._parent().terminator = '"'
        else:
            m = self._re_end_tags[-1].match(line)
            if m is not None:
                # ...</tag>
                if not m.group(1) is None:
                    self._append_text(m.group(1))
                self._end_multiline_tag()
            else:
                # only text, no tags
                self._append_text(line)

    def _init_multiline_tag(self, tag):
        self._append_separator()
        self._parents.append(Node())
        print('"%s":' % tag, end='')
        self._add_re_end_tag(tag)

    def _end_multiline_tag(self):
        print(self._parent().terminator, end='')
        del self._parents[-1]
        self._parent().has_value = True
        del self._re_end_tags[-1]

    def _add_re_end_tag(self, tag):
        pattern = re.compile('^\s*(\S.*)?</%s>\s*$' % tag)
        self._re_end_tags.append(pattern)

    def _parent(self):
        return self._parents[-1]

    def _append_separator(self):
        print(self._parent().separator, end='')

    def _append_text(self, text):
        if text.endswith('\n'):
            print(text[:-1], end=' ')
        else:
            print(text, end='')

