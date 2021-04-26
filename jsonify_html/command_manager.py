from .exceptions import CommandNotFound, RunTimeError
from .utils import singleton
import shlex


@singleton
class CommandManager:
    def __init__(self):
        self.commands = dict()

    def register(self, name, cmd):
        self.commands[name] = cmd

    def run_command(self, name, root, *args, **kwargs):
        if name not in self.commands:
            raise CommandNotFound(f'command `{name}` not found. Did you registered it properly?')
        try:
            return self.commands[name](root, *args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            raise RunTimeError(e)

    def run_command_line(self, cmd_line, root):
        if isinstance(cmd_line, list):
            name = cmd_line[0]
            args = cmd_line[1:-1] if isinstance(cmd_line[-1], dict) else cmd_line[1:]
            kwargs = cmd_line[-1] if isinstance(cmd_line[-1], dict) else dict()
        elif isinstance(cmd_line, str):
            parts = shlex.split(cmd_line)
            name = parts[0]
            args = [arg for arg in parts[1:] if '=' not in arg]
            kwargs = dict(arg.split('=', 1) for arg in parts[1:] if '=' in arg)
        elif isinstance(cmd_line, dict):
            name = list(cmd_line.keys())[0]
            args = cmd_line[name].get("args", [])
            kwargs = {key: value for key, value in cmd_line[name].items() if key != "args"}
        else:
            raise TypeError("Unsupported command type.")
        return self.run_command(name, root, *args, **kwargs)

    def run_command_lines(self, cmd_lines, root):
        for cmd_line in cmd_lines:
            if root is not None:
                root = self.run_command_line(cmd_line, root)
        return root


def register_command(name):
    def decorator(cmd):
        CommandManager().register(name, cmd)
        return cmd
    return decorator
