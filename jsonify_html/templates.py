from .types import *
from .commands import *
import ruamel.yaml as yaml
import re


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
    def __init__(self, file, root):
        pass

    def parse(self, html):
        pass


FUNCTION_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*\([^()]*\)$")
ENTRY_PATTERN = re.compile(r"^([a-zA-Z][a-zA-Z0-9\[\],]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)$")


def parse_variable(name, data):
    value = parse_map(name, Mapping[String, Any], data) if isinstance(data, dict) else data
    return Variable(name, value)


def parse_lambda(data):
    pass


def parse_command(data):
    return Command()


def parse_function(head, data):
    assert isinstance(data, list)
    commands = [parse_command(line) for line in data]
    return Function(commands)


def parse_entry(name, dtype, data):
    if isinstance(data, dict):
        return parse_map(name, as_type(dtype), data)
    elif isinstance(data, list):
        return Node(name, dtype, parse=parse_function("parse()", data))
    else:
        raise ValueError


def parse_map(name, dtype, data):
    children = dict()
    for name, child in data.items():
        name = name.strip()
        match_function = FUNCTION_PATTERN.match(name)
        match_entry = ENTRY_PATTERN.match(name)
        if name.startswith("$"):
            children[name] = parse_variable(name, child)
        elif match_function and isinstance(child, list):
            children[name] = parse_function(name, child)
        elif match_entry:
            entry_type, entry_name = match_entry.groups()
            children[name] = parse_entry(entry_name, entry_type, child)
        else:
            raise ValueError
    return Node(name, dtype, **children)


def parse_template(template):
    data = yaml.round_trip_load(template)
    assert isinstance(data, dict)
    root = parse_map("<template>", Mapping[String, Any], data)
    return Template(template, root)
