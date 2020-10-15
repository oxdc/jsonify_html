from ..base import JsonifyCommand
from ..parser import parse_template
from ..template_manager import get_template


class CMDForEach(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.sub_template = get_template(args[0]) if isinstance(args[0], str) else args[0]

    def execute(self):
        return [parse_template(self.sub_template, element) for element in self.root]
