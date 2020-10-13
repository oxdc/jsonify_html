from .base import JsonifyCommand


class CMDRun(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.cmd_type = args[0]
        self.cmd_args = args[1:]

    def execute(self):
        if self.cmd_type == 'exec':
            for cmd in self.cmd_args:
                exec(cmd.replace('$root', 'self.root').replace('$output', 'last_output'))
            return self.root
        elif self.cmd_type == 'eval':
            last_output = self.root
            for cmd in self.cmd_args:
                last_output = eval(cmd.replace('$root', 'self.root').replace('$output', 'last_output'))
            return last_output
        elif self.cmd_type == 'script':
            raise NotImplementedError
