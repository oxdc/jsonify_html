from dataclasses import dataclass


@dataclass
class Mark:
    file = "::memory::"
    line = 0
    column = 0
