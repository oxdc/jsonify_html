from ..base import JsonifyCommand
from urllib.parse import quote


class CMDQuote(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)

    def execute(self):
        return quote(self.root)
