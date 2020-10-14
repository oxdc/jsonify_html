from ..base import JsonifyCommand


class CMDConcatString(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.mode = args[0]
        self.sep = args[1]
        self.to_concat = args[2:]

    def execute(self):
        if self.mode in ['pre', 'prefix']:
            return self.sep.join([*self.to_concat, self.root])
