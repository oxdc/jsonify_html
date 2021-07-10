from .types import *
from .mark import Mark


class Variable:
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
    #
    # def parse(self, parent, entry):
    #     assert entry.startswith("$")
    #     self.name = entry
    #     self.value = parent.get(entry)
    #

class Function:
    pass


class Lambda:
    pass
