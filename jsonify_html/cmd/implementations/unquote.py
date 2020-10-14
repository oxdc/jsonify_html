from ..base import JsonifyCommand
from urllib.parse import unquote


class CMDUnquote(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)

    def execute(self):
        return unquote(self.root)
