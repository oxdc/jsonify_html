from .base import JsonifyCommand
from .exceptions import CommandTypeError, CommandNotFound
from .utils import singleton


@singleton
class CommandManager:
    def __init__(self):
        self.commands = dict()

    def register(self, name, cls):
        if not issubclass(cls, JsonifyCommand):
            raise CommandTypeError('unrecognizable command.')
        self.commands[name] = cls

    def run_command(self, cmd, args, root):
        if cmd not in self.commands:
            raise CommandNotFound(f'command `{cmd}` not found. Did you registered it properly?')
        return self.commands[cmd](root, args).execute()

    def run_commands(self, cmd_lines, root):
        for cmd_line in cmd_lines:
            root = self.run_command(cmd_line[0], cmd_line[1:], root)
        return root


def register_command(cls, *, name):
    CommandManager().register(name, cls)
    return CommandManager()
