from ..base import JsonifyCommand
from lxml.html import tostring, fromstring
from htmlmin.minify import html_minify
import re


multiple_spaces = re.compile(r'\s\s+')


class CMDMinifyHTML(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)

    def execute(self):
        html = tostring(self.root).decode('utf-8').replace('\n', '')
        html = html_minify(html, parser='lxml')
        return fromstring(multiple_spaces.sub(' ', html)).body[0]
