from inspect import getmembers, isfunction
from struct import pack, unpack
from .utils import singleton


class DataType:
    def convert(self, obj):
        return obj


Any = DataType()


@singleton
class UndefinedType(DataType):
    def convert(self, obj):
        return None


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
        pass


DateTime = DateTimeType()


TYPES = {
    "Any": Any,
    "Boolean": Boolean,
    "Bool": Bool,
    "Integer": Integer,
    "BigInt": BigInt,
    "Int": Int,
    "Char": Char,
    "Int8": Int8,
    "UChar": UChar,
    "UInt8": UInt8,
    "Int16": Int16,
    "UInt16": UInt16,
    "Int32": Int32,
    "UInt32": UInt32,
    "Int64": Int64,
    "UInt64": UInt64,
    "Int128": Int128,
    "UInt128": UInt128,
    "Int256": Int256,
    "UInt256": UInt256,
    "Float16": Float16,
    "Float32": Float32,
    "Float64": Float64,
    "Text": Text,
    "String": String,
    "Str": Str,
    "List": List,
    "HashTable": HashTable,
    "Dictionary": Dictionary,
    "Dict": Dict,
    "Mapping": Mapping,
    "Object": Object,
    "Set": Set,
    "Tuple": Tuple,
    "DateTime": DateTime
}


def as_type(type_name):
    if isinstance(type_name, DataType):
        return type_name
    else:
        return TYPES[str(type_name)]


class Variable:
    def __init__(self, name, value=undefined):
        self.name = name
        self.value = value


class Ref:
    def __init__(self, name):
        self.name = name
