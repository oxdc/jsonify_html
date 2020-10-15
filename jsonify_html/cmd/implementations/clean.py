from ..base import JsonifyCommand
from lxml.html.clean import Cleaner


class CMDClean(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.options = args[0] if len(args) > 0 else dict()

    def execute(self):
        return Cleaner(**self.options).clean_html(self.root)
