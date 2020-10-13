from .base import JsonifyCommand


class CMDStrip(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)

    def execute(self):
        return self.root.strip() if isinstance(self.root, str) else str(self.root).strip()
