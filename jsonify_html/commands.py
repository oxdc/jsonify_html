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

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__.get(key, undefined)

    def extend(self, other):
        for key, value in other.__dict__.items():
            self.__dict__[key] = value


global_env = Environment()


class Command:
    def __repr__(self):
        return f"Command<{type(self).__name__}>"

    def __call__(self, _root, *args, **kwargs):
        raise NotImplementedError


class Function:
    def __init__(self, name, argv=None, commands=None, *, node=None):
        self.name = name
        self.__node = node
        self.argv = argv or []
        self.commands = commands or []

    def bind(self, node):
        self.__node = node

    def __call__(self, *args, **kwargs):
        assert self.__node is not None
        for command in self.commands:
            for arg in self.argv:
                kwargs[arg] = self.__node.locals[arg]
            self.__node.root = command(self.__node.root, *args, **kwargs)
        return self.__node.root
