from ..base import JsonifyCommand


class CMDInnerText(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)

    def execute(self):
        return self.root.xpath('string()')
