from ..base import JsonifyCommand
from lxml.cssselect import CSSSelector


class CMDDeleteAttributes(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.implementation = args[0]
        self.selector = args[1]
        self.xpath = self.selector if self.implementation in ['x', 'xpath'] else CSSSelector(self.selector).path
        self.to_delete = args[2:]

    def execute(self):
        for el in self.root.xpath(self.xpath):
            for attr in self.to_delete:
                if attr in el.attrib:
                    del el.attrib[attr]
        return self.root
