from .types import undefined


class Environment:
    def __init__(self, **variables):
        self.__variables = variables

    def clear(self):
        self.__variables.clear()

    def __setattr__(self, key, value):
        self.__variables[key] = value

    def __getattr__(self, key):
        return self.__variables.get(key, undefined)


global_env = Environment()


class Command:
    def __repr__(self):
        return f"Command<{type(self).__name__}>"

    def __call__(self, _root, *args, **kwargs):
        raise NotImplementedError
