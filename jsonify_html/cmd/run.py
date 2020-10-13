from .base import JsonifyCommand


class CMDRun(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.cmd_type = args[0]
        self.cmd_args = args[1:]

    def execute(self):
        if self.cmd_type == 'inline':
            last_output = None
            for cmd in self.cmd_args:
                last_output = eval(cmd.replace('$root', 'self.root').replace('$output', 'last_output'))
            return last_output
        elif self.cmd_type == 'script':
            raise NotImplementedError
