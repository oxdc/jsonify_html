import re


# class CommandManager:
#     def parse_arg(self, arg):
#         if '=' in arg:
#             return [kv.strip() for kv in arg.split('=')]
#         elif '->' in arg:
#             pass
#         else:
#             return arg.strip()
#
#     def parse_arg_list(self, arg_list):
#         re.split(r"\s*,\s*", arg_list)
#
#     def parse_cmd(self, statement):
#         name, arg_list = re.fullmatch(r"([a-zA-Z_]+)\(([^()]*)\)", statement.strip()).groups()
#         args, kwargs = self.parse_arg_list(arg_list)


class Command:
    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs

    @classmethod
    def __cmd_name(cls):
        return cls.__name__

    def __repr__(self):
        args = ", ".join(repr(arg) for arg in self.__args)
        kwargs = ", ".join(f"{key}={repr(value)}" for key, value in self.__kwargs.items())
        if kwargs:
            return f"Command<{self.__cmd_name()}>({args}; {kwargs})"
        else:
            return f"Command<{self.__cmd_name()}>({args})"

    def parse(self, statement):
        raise NotImplementedError

    def execute(self, root):
        raise NotImplementedError


def register_command(name):
    def decorator(cmd):
        CommandManager().register(name, cmd)
        return cmd
    return decorator
