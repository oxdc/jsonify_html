from .types import *


class Node:
    def __init__(self, name, dtype, **kwargs):
        self.name = name
        self.dtype = as_type(dtype)
        self.__root = None
        self.__methods = list()
        self.__attributes = dict()
        for name, value in kwargs.items():
            if callable(value):
                setattr(self, name, lambda *_args, **_kwargs: value(self.__root, *_args, **_kwargs))
                self.__methods.append(name)
            else:
                self.__attributes[name] = value

    @property
    def root(self):
        return self.__root

    @root.setter
    def root(self, root):
        self.__root = root

    def call(self, method, *args, **kwargs):
        if hasattr(self, method):
            self.__root = getattr(self, method)(*args, **kwargs)

    def execute(self):
        self.call("init")
        self.call("parse")
        if isa(self.dtype, MapType):
            pairs = [(name, node.execute()) for name, node in self.__attributes.items()]
            result = self.dtype.convert(pairs)
        else:
            result = self.dtype.convert(self.__root)
        self.call("final")
        return result


class Package:
    pass


class Template:
    pass
