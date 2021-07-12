from .types import *
from .commands import build_in_commands
import ruamel.yaml as yaml
import re


class Function:
    def __init__(self, arg_names, commands):
        self.node = None
        self.arg_names = arg_names
        self.args = {arg: None for arg in arg_names}
        self.commands = commands or []

    def __from_node(self, arg):
        return self.node.get_variable(arg) if isinstance(arg, Ref) else arg

    def __from_local(self, arg):
        return self.node.get_variable(arg) or self.args.get(arg.name, None) if isinstance(arg, Ref) else arg

    def parse_args(self, args, kwargs):
        for name, arg in zip(self.arg_names, args):
            self.args[name] = self.__from_node(arg)
        for name, arg in kwargs.items():
            assert name in self.arg_names
            self.args[name] = self.__from_node(arg)

    def __call__(self, node, *args, **kwargs):
        self.node = node
        assert self.node is not None
        assert len(args) + len(kwargs) <= len(self.arg_names)
        self.parse_args(args, kwargs)
        for cmd, cmd_args, cmd_kwargs in self.commands:
            func = self.node.get_cmd(cmd)
            _args = [self.__from_local(arg) for arg in cmd_args]
            _kwargs = {key: self.__from_local(arg) for key, arg in cmd_kwargs.items()}
            self.node.root = func(self.node.root, *_args, **_kwargs)
        return self.node.root


trivial_function = Function([], [])


class Node:
    def __init__(self, dtype, attributes):
        self.dtype = as_type(dtype)
        self.root = None
        self.children = dict()
        self.init = attributes.pop("init", trivial_function)
        self.parse = attributes.pop("parse", trivial_function)
        self.final = attributes.pop("final", trivial_function)
        self.variables = dict()
        self.methods = dict()
        self.__registered_commands = build_in_commands
        for name, value in attributes.items():
            if isinstance(value, Function):
                self.methods[name] = value
            elif isinstance(value, Node) and isinstance(self.dtype, MapType):
                self.children[name] = value
            elif isinstance(value, Variable):
                self.variables[name] = value
            else:
                raise AttributeError
        for node in self.children.values():
            node.variables.update(self.variables)
            node.methods.update(self.methods)

    def get_cmd(self, cmd):
        return self.methods.get(cmd, None) or self.__registered_commands.get(cmd, None)

    def get_variable(self, ref):
        return self.variables.get(ref.name, Variable(ref.name, undefined))

    def execute(self):
        self.init(self)
        if isinstance(self.dtype, MapType):
            for child in self.children.values():
                child.root = self.root
        self.parse(self)
        if isinstance(self.dtype, MapType):
            pairs = [(name, node.execute()) for name, node in self.children.items()]
            result = self.dtype.convert(pairs)
        else:
            result = self.dtype.convert(self.root)
        self.final(self)
        return result


VARIABLE_PATTERN = re.compile(r"^\$([a-zA-Z_][a-zA-Z0-9_]*)$")
FUNCTION_PATTERN = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\(([^()]*)\)$")
LAMBDA_PATTERN = re.compile(r"->")  # TODO
ENTRY_PATTERN = re.compile(r"^([a-zA-Z][a-zA-Z0-9\[\],]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)$")
COMMA_PATTERN = re.compile(r",(?![^(]*\))")


def parse_variable(name, data):
    value = parse_map(Object, data) if isinstance(data, dict) else data
    return Variable(name, value)


def parse_arg(arg):
    match_variable = VARIABLE_PATTERN.match(arg)
    match_lambda = LAMBDA_PATTERN.match(arg)
    if match_variable:
        name, = match_variable.groups()
        return Ref(name)
    elif match_lambda:
        return lambda x: x  # TODO
    else:
        return yaml.safe_load(arg)


def parse_args(data):
    args = list()
    kwargs = dict()
    for item in data:
        if not item.strip():
            continue
        if '=' in item:
            name, arg = item.split('=')
            kwargs[name.strip()] = parse_arg(arg.strip())
        else:
            args.append(parse_arg(item.strip()))
    return args, kwargs


def parse_command(data):
    cmd, arg_list = FUNCTION_PATTERN.match(data).groups()
    args, kwargs = parse_args(COMMA_PATTERN.split(arg_list))
    return cmd, args, kwargs


def parse_function(arg_list, data):
    arg_names = [arg.strip() for arg in arg_list.split(",")]
    assert isinstance(data, list)
    commands = [parse_command(line) for line in data]
    return Function(arg_names, commands)


def parse_entry(dtype, data):
    if isinstance(data, dict):
        return parse_map(dtype, data)
    elif isinstance(data, list):
        return Node(dtype, {"parse": parse_function("", data)})
    else:
        raise ValueError


def parse_map(dtype, data):
    attributes = dict()
    for head, child in data.items():
        head = head.strip()
        match_variable = VARIABLE_PATTERN.match(head)
        match_function = FUNCTION_PATTERN.match(head)
        match_entry = ENTRY_PATTERN.match(head)
        if match_variable:
            name, = match_variable.groups()
            attributes[name] = parse_variable(name, child)
        elif match_function and isinstance(child, list):
            name, arg_list = match_function.groups()
            attributes[name] = parse_function(arg_list, child)
        elif match_entry:
            entry_dtype, name = match_entry.groups()
            attributes[name] = parse_entry(entry_dtype, child)
        else:
            raise ValueError
    return Node(dtype, attributes)


def parse_template(template):
    data = yaml.round_trip_load(template)
    assert isinstance(data, dict)
    root = parse_map(Object, data)
    return root
