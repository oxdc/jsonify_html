from ..base import JsonifyCommand
from lxml.html import tostring, fromstring


class CMDDeleteWhitespace(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)

    def execute(self):
        return fromstring(
            tostring(self.root)
                .decode('utf-8')
                .replace('\n', '')
                .replace('&#09;', '')
                .replace('&#10;', '')
                .replace('&#13;', '')
                .replace('&#160;', '')
        )
