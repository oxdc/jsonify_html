from .types import *
from .commands import *


class Variable:
    def __init__(self, name, value=undefined):
        self.name = name
        self.value = value


class Node:
    def __init__(self, name, dtype, **kwargs):
        self.name = name
        self.dtype = as_type(dtype)
        self.root = None
        self.children = dict()
        self.locals = Environment()
        self.__methods = list()
        for name, value in kwargs.items():
            if isinstance(value, Function):
                value.bind(self)
                setattr(self, name, value)
                self.__methods.append(name)
            elif isinstance(value, Node) and isinstance(self.dtype, MapType):
                self.children[name] = value
            elif isinstance(value, Variable):
                self.locals.name = value
            else:
                raise AttributeError

    def call(self, method, *args, **kwargs):
        if hasattr(self, method):
            self.root = getattr(self, method)(*args, **kwargs)

    def execute(self):
        self.call("init")
        if isinstance(self.dtype, MapType):
            for child in self.children.values():
                child.root = self.root
        self.call("parse")
        if isinstance(self.dtype, MapType):
            pairs = [(name, node.execute()) for name, node in self.children.items()]
            result = self.dtype.convert(pairs)
        else:
            result = self.dtype.convert(self.root)
        self.call("final")
        return result


class Package:
    pass


class Template:
    pass
