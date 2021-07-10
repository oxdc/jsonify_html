from inspect import getmembers, isfunction
from struct import pack, unpack


class DataType:
    def convert(self, obj):
        return obj


Any = DataType()


class __BoolType(DataType):
    def convert(self, obj):
        return bool(obj)


Boolean = Bool = __BoolType()


class __IntType(DataType):
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


Integer = BigInt = Int = __IntType()
Char = Int8 = __IntType(size=8, signed=True)
UChar = UInt8 = __IntType(size=8, signed=False)
Int16 = __IntType(size=16, signed=True)
UInt16 = __IntType(size=16, signed=False)
Int32 = __IntType(size=32, signed=True)
UInt32 = __IntType(size=32, signed=False)
Int64 = __IntType(size=64, signed=True)
UInt64 = __IntType(size=64, signed=False)
Int128 = __IntType(size=128, signed=True)
UInt128 = __IntType(size=128, signed=False)
Int256 = __IntType(size=256, signed=True)
UInt256 = __IntType(size=256, signed=False)


class __FloatType(DataType):
    def __init__(self, fmt=None):
        self.fmt = fmt

    def convert(self, obj):
        if self.fmt:
            return unpack(self.fmt, pack(self.fmt, float(obj)))[0]
        else:
            return float(obj)


Float16 = __FloatType(fmt="<e")
Float32 = __FloatType(fmt="<f")
Float64 = __FloatType(fmt="<d")


class __StringType(DataType):
    def convert(self, obj):
        return str(obj)


Text = String = Str = __StringType()


class __ListType(DataType):
    def __init__(self, etype=None):
        self.etype = etype

    def __getitem__(self, etype):
        self.etype = etype
        return self

    def convert(self, obj):
        return [self.etype.convert(item) for item in iter(obj)]


List = __ListType()


class __MapType(DataType):
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


HashTable = Dictionary = Dict = Mapping = __MapType()


class __SetType(DataType):
    def __init__(self):
        self.etype = None

    def __getitem__(self, etype):
        self.etype = etype
        return self

    def convert(self, obj):
        return {self.etype.convert(item) for item in iter(obj)}


Set = __SetType()


class __TupleType(DataType):
    def __init__(self, *types):
        self.types = types

    def __getitem__(self, types):
        self.types = types
        return self

    def convert(self, obj):
        return tuple(etype.convert(item) for etype, item in zip(self.types, iter(obj)))


Tuple = __TupleType()
