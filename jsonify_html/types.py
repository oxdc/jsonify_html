from inspect import getmembers, isfunction
from struct import pack, unpack
from dateutil import parser as date_parser
from .utils import singleton


class DataType:
    def convert(self, obj):
        return obj


Any = DataType()


@singleton
class UndefinedType(DataType):
    def convert(self, obj):
        return None

    def __bool__(self):
        return False


undefined = Undefined = UndefinedType()


class BoolType(DataType):
    def convert(self, obj):
        return bool(obj)


Boolean = Bool = BoolType()


class IntType(DataType):
    def __init__(self, *, size=None, signed=True):
        self.size = size // 8 if size else None
        self.signed = signed

    def convert(self, obj):
        if isinstance(obj, str) and obj.startswith("0x"):
            result = int(obj, base=16)
        elif isinstance(obj, str) and obj.startswith("0o"):
            result = int(obj, base=8)
        elif isinstance(obj, str) and obj.startswith("0b"):
            result = int(obj, base=2)
        else:
            result = int(obj)
        if self.size:
            return int.from_bytes(
                result.to_bytes(self.size, "little", signed=self.signed),
                "little", signed=self.signed)
        else:
            return result


Integer = BigInt = Int = IntType()
Char = Int8 = IntType(size=8, signed=True)
UChar = UInt8 = IntType(size=8, signed=False)
Int16 = IntType(size=16, signed=True)
UInt16 = IntType(size=16, signed=False)
Int32 = IntType(size=32, signed=True)
UInt32 = IntType(size=32, signed=False)
Int64 = IntType(size=64, signed=True)
UInt64 = IntType(size=64, signed=False)
Int128 = IntType(size=128, signed=True)
UInt128 = IntType(size=128, signed=False)
Int256 = IntType(size=256, signed=True)
UInt256 = IntType(size=256, signed=False)


class FloatType(DataType):
    def __init__(self, fmt=None):
        self.fmt = fmt

    def convert(self, obj):
        if self.fmt:
            return unpack(self.fmt, pack(self.fmt, float(obj)))[0]
        else:
            return float(obj)


Float16 = FloatType(fmt="<e")
Float32 = FloatType(fmt="<f")
Float64 = FloatType(fmt="<d")


class StringType(DataType):
    def convert(self, obj):
        return str(obj)


Text = String = Str = StringType()


class ListType(DataType):
    def __init__(self, etype=None):
        self.etype = etype

    def __getitem__(self, etype):
        self.etype = etype
        return self

    def convert(self, obj):
        return [self.etype.convert(item) for item in iter(obj)]


List = ListType()


class MapType(DataType):
    def __init__(self, ktype=None, vtype=None):
        self.ktype = ktype
        self.vtype = vtype

    def __getitem__(self, types):
        self.ktype, self.vtype = types
        return self

    def convert(self, obj):
        if "items" in map(lambda pair: pair[0], getmembers(type(obj), predicate=isfunction)):
            return {self.ktype.convert(key): self.vtype.convert(value) for key, value in obj.items()}
        else:
            return {self.ktype.convert(key): self.vtype.convert(value) for key, value in iter(obj)}


HashTable = Dictionary = Dict = Mapping = MapType()
Object = Mapping[String, Any]


class SetType(DataType):
    def __init__(self):
        self.etype = None

    def __getitem__(self, etype):
        self.etype = etype
        return self

    def convert(self, obj):
        return {self.etype.convert(item) for item in iter(obj)}


Set = SetType()


class TupleType(DataType):
    def __init__(self, *types):
        self.types = types

    def __getitem__(self, types):
        self.types = types
        return self

    def convert(self, obj):
        return tuple(etype.convert(item) for etype, item in zip(self.types, iter(obj)))


Tuple = TupleType()


class DateTimeType(DataType):
    def convert(self, obj):
        return date_parser.parse(obj)


DateTime = DateTimeType()


def as_type(type_name):
    if isinstance(type_name, DataType):
        return type_name
    else:
        dtype = eval(type_name)
        assert isinstance(dtype, DataType)
        return dtype


class Variable:
    def __init__(self, name, value=undefined):
        self.name = name
        self.value = value

    def __str__(self):
        return f"${self.name} = {self.value}"

    def __bool__(self):
        return self.value is not undefined


class Ref:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"${self.name}"


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

    def __parse_args(self, args, kwargs):
        for name, arg in zip(self.arg_names, args):
            self.args[name] = self.__from_node(arg)
        for name, arg in kwargs.items():
            assert name in self.arg_names
            self.args[name] = self.__from_node(arg)

    def __convert_ref(self, args, kwargs):
        _args = [Ref(arg) if arg in self.arg_names else arg for arg in args]
        _kwargs = {key: Ref(arg) if arg in self.arg_names else arg for key, arg in kwargs.items()}
        return _args, _kwargs

    def __resolve_ref(self, args, kwargs):
        _args = [self.__from_local(arg) for arg in args]
        _kwargs = {key: self.__from_local(arg) for key, arg in kwargs.items()}
        return _args, _kwargs

    def __call__(self, node, *args, **kwargs):
        self.node = node
        assert self.node is not None
        assert len(args) + len(kwargs) <= len(self.arg_names)
        self.__parse_args(args, kwargs)
        for cmd, cmd_args, cmd_kwargs in self.commands:
            func = self.node.get_cmd(cmd)
            _args, _kwargs = self.__resolve_ref(*self.__convert_ref(cmd_args, cmd_kwargs))
            self.node.root = func(self.node, *_args, **_kwargs)
        return self.node.root

    def __str__(self):
        arg_str = ", ".join(self.arg_names)
        cmd_str = "; ".join(cmd for cmd, _, _ in self.commands)
        return f"({arg_str}) -> {{{cmd_str}}}"


trivial_function = Function([], [])
