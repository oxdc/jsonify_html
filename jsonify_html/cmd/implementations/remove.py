from ..base import JsonifyCommand
from ..exceptions import ArgumentError
from lxml.cssselect import CSSSelector


class CMDRemove(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.implementation, self.selector = args

    @staticmethod
    def remove_preserve_tail(element):
        prev = element.getprevious()
        parent = element.getparent()
        if element.tail:
            if prev is not None:
                prev.tail = (prev.tail or '') + element.tail
            else:
                parent.text = (parent.text or '') + element.tail
        parent.remove(element)

    def execute(self):
        if self.implementation in ['x', 'xpath']:
            xpath = self.selector
        elif self.implementation in ['css', 'c']:
            xpath = CSSSelector(self.selector).path
        else:
            raise ArgumentError('invalid selector implementation.')
        for element in self.root.xpath(xpath):
            self.remove_preserve_tail(element)
        return self.root
