import ruamel.yaml as yaml
import re
from copy import deepcopy
from .types import *
from .commands import CommandManager


class Node:
    def __init__(self, dtype, attributes):
        self.dtype = as_type(dtype)
        self.root = None
        self.children = dict()
        self.init = attributes.pop("init", trivial_function)
        self.parse = attributes.pop("parse", trivial_function)
        self.final = attributes.pop("final", trivial_function)
        self.__variables = dict()
        self.__methods = dict()
        self.__registered_commands = CommandManager().commands
        for name, value in attributes.items():
            if isinstance(value, Function):
                self.__methods[name] = value
            elif isinstance(value, Node) and isinstance(self.dtype, MapType):
                self.children[name] = value
            elif isinstance(value, Variable):
                self.__variables[name] = value
            else:
                print(name, value)
                raise AttributeError
        for node in self.children.values():
            node.update_variables(self.__variables)
            node.update_methods(self.__methods)

    @property
    def variables(self):
        return self.__variables

    @property
    def methods(self):
        return self.__methods

    def update_variables(self, variables):
        self.__variables.update(variables)
        for node in self.children.values():
            node.update_variables(self.__variables)

    def update_methods(self, methods):
        self.__methods.update(methods)
        for node in self.children.values():
            node.update_methods(self.__methods)

    def get_cmd(self, cmd):
        return self.__methods.get(cmd, None) or self.__registered_commands.get(cmd, None)

    def get_variable(self, ref):
        return self.__variables.get(ref.name, Variable(ref.name, undefined))

    def execute(self):
        self.init(self)
        if isinstance(self.dtype, MapType):
            for child in self.children.values():
                child.root = deepcopy(self.root)
        self.parse(self)
        if isinstance(self.dtype, MapType):
            pairs = [(name, node.execute()) for name, node in self.children.items()]
            result = self.dtype.convert(pairs)
        else:
            result = self.dtype.convert(self.root)
        self.final(self)
        return result


VARIABLE_PATTERN = re.compile(r"^\$([a-zA-Z_][a-zA-Z0-9_]*)$")
FUNCTION_PATTERN = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\((.*?)\)$")
LAMBDA_PATTERN = re.compile(r"^\(*([^()]*)\)*\s*->\s*([a-zA-Z0-9_]+)\((.*)\)$")
ENTRY_PATTERN = re.compile(r"^([a-zA-Z][a-zA-Z0-9\[\],]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)$")
KEYWORD_ARGUMENT_PATTERN = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$")


def parse_variable(name, data):
    value = parse_map(Object, data) if isinstance(data, dict) else data
    return Variable(name, value)


def parse_arg(arg):
    match_variable = VARIABLE_PATTERN.match(arg)
    match_lambda = LAMBDA_PATTERN.match(arg)
    match_function = FUNCTION_PATTERN.match(arg)
    if match_variable:
        name, = match_variable.groups()
        return Ref(name)
    elif match_lambda:
        head, cmd, arg_list = match_lambda.groups()
        arg_names = [arg.strip() for arg in head.split(",")]
        args, kwargs = parse_args(split_at_comma(arg_list))
        return Function(arg_names, [(cmd, args, kwargs)])
    elif match_function:
        return Function([], [parse_command(arg)])
    else:
        return yaml.safe_load(arg)


def parse_args(data):
    args = list()
    kwargs = dict()
    for item in data:
        match_kw = KEYWORD_ARGUMENT_PATTERN.match(item.strip())
        if not item.strip():
            continue
        if match_kw:
            name, arg = match_kw.groups()
            kwargs[name.strip()] = parse_arg(arg.strip())
        else:
            args.append(parse_arg(item.strip()))
    return args, kwargs


def grouped(iterable, n):
    return zip(*[iter(iterable)]*n)


def scan_for_comma(s):
    poses = [0]
    level_single_quote = 0
    level_double_quote = 0
    level_square_bracket = 0
    level_round_bracket = 0
    level_curly_bracket = 0
    max_level = 0
    for pos, char in enumerate(s):
        if char == '\'':
            level_single_quote = (level_single_quote + 1) % 2
        elif char == '"':
            level_double_quote = (level_double_quote + 1) % 2
        elif char == '[':
            level_square_bracket += 1
        elif char == ']':
            level_square_bracket -= 1
        elif char == '(':
            level_round_bracket += 1
        elif char == ')':
            level_round_bracket -= 1
        elif char == '{':
            level_curly_bracket += 1
        elif char == '}':
            level_curly_bracket -= 1
        max_level = max(level_single_quote, level_double_quote,
                        level_square_bracket, level_round_bracket, level_curly_bracket)
        if char == ',' and max_level == 0:
            poses.append(pos)
            poses.append(pos+1)
    assert max_level == 0
    poses.append(len(s))
    return poses


def split_at_comma(s):
    poses = scan_for_comma(s)
    return [s[start:end] for start, end in grouped(poses, 2)]


def parse_command(data):
    cmd, arg_list = FUNCTION_PATTERN.match(data).groups()
    args, kwargs = parse_args(split_at_comma(arg_list))
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
