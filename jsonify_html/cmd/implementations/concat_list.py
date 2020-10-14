from ..base import JsonifyCommand


class CMDConcatList(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)

    def execute(self):
        result = []
        for item in self.root:
            if isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result
