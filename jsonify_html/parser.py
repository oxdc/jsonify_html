import json
from .cmd import COMMANDS


class JsonifyHtml:
    def __init__(self, template, html):
        with open(template) as template_reader:
            self.template = json.load(template_reader)
        self.html = html

    def parse(self):
        for key, content in self.template.items():
            pass
