from ..base import JsonifyCommand
import re


class CMDRegex(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.flag = args[0]
        self.cmd = args[1]
        self.pattern = re.compile(args[2])
        if self.cmd == 'replace':
            self.replace = args[3].replace('$', '\\')
        elif self.cmd == 'get_group':
            self.get_group = int(args[3])

    def execute(self):
        if self.cmd == 'replace':
            return self.pattern.sub(self.root, self.replace)
        elif self.cmd == 'get_group':
            return self.pattern.search(self.root).group(self.get_group)
