from .types import undefined


class Environment:
    def __init__(self, **variables):
        self.__dict__ = variables

    def clear(self):
        self.__dict__.clear()

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, key):
        return self.__dict__.get(key, undefined)


global_env = Environment()


class Command:
    def __repr__(self):
        return f"Command<{type(self).__name__}>"

    def __call__(self, _root, *args, **kwargs):
        raise NotImplementedError


class Function:
    def __init__(self, node=None, commands=None):
        self.__node = node
        self.commands = commands if commands is not None else []

    def bind(self, node):
        self.__node = node

    def __call__(self, *args, **kwargs):
        pass
