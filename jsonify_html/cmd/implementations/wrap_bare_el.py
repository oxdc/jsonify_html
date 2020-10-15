from ..base import JsonifyCommand
from lxml.html import tostring, fromstring
from lxml.cssselect import CSSSelector


class CMDWrapBareElement(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.tag = args[0]
        self.attributes = args[1]
        self.method = args[2]
        self.bypass_els = args[3:]
        if self.method in ['c', 'css']:
            self.bypass_els = [CSSSelector(selector).path for selector in self.bypass_els]

    def match_bypass(self, el):
        for xpath in self.bypass_els:
            if el in self.root.xpath(xpath):
                return True
        return False

    def execute(self):
        copy = fromstring(tostring(self.root))
        for child in copy:
            if self.match_bypass(child):
                copy.remove(child)
        copy.tag = self.tag
        for key, value in self.attributes.items():
            copy.attrib[key] = value
        return copy
