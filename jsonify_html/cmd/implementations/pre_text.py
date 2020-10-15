from ..base import JsonifyCommand


class CMDPreText(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)

    def execute(self):
        return self.root.text or ''
