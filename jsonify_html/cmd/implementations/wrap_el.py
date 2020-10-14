from ..base import JsonifyCommand
from lxml.html import Element


class CMDWarpElement(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.tag = args[0]
        self.attributes = args[1]

    def execute(self):
        parent = Element(self.tag, **self.attributes)
        parent.insert(0, self.root)
        return parent
