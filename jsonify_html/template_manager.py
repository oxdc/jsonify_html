from .utils import singleton
from .exceptions import DuplicatedRegister
from .parser.selector import parse_selector


@singleton
class TemplateCache:
    def __init__(self):
        self.cache = dict()
        self.matches = dict()

    def register(self, name, template):
        if name in self.cache:
            raise DuplicatedRegister(f'duplicated template found: `{name}`.')
        self.cache[name] = template
        if '$match' in template:
            selector = parse_selector(template['$match'])
            self.matches[name] = selector

    def delete(self, name):
        del self.cache[name]

    def get_by_name(self, name):
        if name not in self.cache:
            raise FileNotFoundError(f'required template `{name}` not found.')
        return self.cache[name]

    def get_by_match(self, root):
        parent = root.getparent()
        return [self.cache[name] for name, selector in self.matches.items() if root in parent.xpath(selector)]
