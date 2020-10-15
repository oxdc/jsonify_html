from ..base import JsonifyCommand
from ..parser import parse_template


class CMDApply(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.sub_template = args[0]

    def execute(self):
        return parse_template(self.sub_template, self.root)
