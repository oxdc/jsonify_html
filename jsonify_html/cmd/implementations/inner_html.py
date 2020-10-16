from ..base import JsonifyCommand
from lxml.html import tostring, fromstring


class CMDInnerHTML(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)

    def execute(self):
        return fromstring(''.join(tostring(child).decode('utf-8') for child in self.root)) \
            if self.root is not None and len(self.root) else None
