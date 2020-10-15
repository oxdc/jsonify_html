import json
from .utils import singleton
import re


include_statement = re.compile(r'\s*\$include\(\s*([^()\s]+)\s*\)\s*')


@singleton
class TemplateCache:
    def __init__(self):
        self.cache = dict()

    def register(self, name, template):
        self.cache[name] = template

    def delete(self, name):
        del self.cache[name]

    def get(self, name):
        if name not in self.cache:
            raise FileNotFoundError(f'required template `{name}` not found.')
        return self.cache[name]


def cache_template(templates):
    for name, file in templates.items():
        with open(file, encoding='utf-8') as file_reader:
            TemplateCache().register(name, json.load(file_reader))
    return TemplateCache()


def get_template(statement, merge=True):
    names = include_statement.findall(statement)
    templates = [TemplateCache().get(name) for name in names]
    if not merge:
        return templates
    else:
        template = dict()
        for cached in templates:
            template = {**template, **cached}
        return template
