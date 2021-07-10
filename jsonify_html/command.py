class ExecutionError(Exception):
    def __init__(self, file, line, column, message):
        self.file = file
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return f"{self.message}, line {self.line}, column {self.column}, in {self.file}"


class Command:
    def __init__(self, *args, **kwargs):
        self.name = "BaseCommand"
        self.__args = args
        self.__kwargs = kwargs

    def __repr__(self):
        args = ", ".join(repr(arg) for arg in self.__args)
        kwargs = ", ".join(f"{key}={repr(value)}" for key, value in self.__kwargs.items())
        if kwargs:
            return f"Command<{self.name}>({args}; {kwargs})"
        else:
            return f"Command<{self.name}>({args})"

    def parse(self, statement):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError
