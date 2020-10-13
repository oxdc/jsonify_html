from .base import JsonifyCommand
from .exceptions import ArgumentError
from lxml.cssselect import CSSSelector


class CMDSelect(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.implementation, self.selector = args

    def execute(self):
        if self.implementation in ['x', 'xpath']:
            xpath = self.selector
        elif self.implementation in ['css', 'c']:
            xpath = CSSSelector(self.selector).path
        else:
            raise ArgumentError('invalid selector implementation.')
        return self.root.xpath(xpath)
