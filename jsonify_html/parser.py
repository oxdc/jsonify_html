import json
from .cmd import COMMANDS
from lxml.html.html5parser import fromstring
from lxml.html import parse


class JsonifyHtml:
    def __init__(self, *, template_file=None, template=None, html_file=None, html=None, encoding='utf-8'):
        if template_file is not None:
            with open(template_file) as template_reader:
                self.template = json.load(template_reader)
        elif template is not None:
            self.template = template
        else:
            raise Exception('no template given.')
        if html_file is not None:
            with open(html_file, encoding=encoding) as html_reader:
                self.html = html_reader.read()
            self.page = parse(html_file)
        elif html is not None:
            self.html = html
            self.page = fromstring(self.html)
        else:
            raise Exception('empty html.')

    def parse(self):
        obj = dict()
        for key, content in self.template.items():
            root = self.page
            for cmdline in content['cmd']:
                cmd = cmdline[0]
                args = cmdline[1:]
                root = COMMANDS[cmd](root, args).execute()
            obj[key] = self.convert_type(content['type'], root)
        return obj

    @staticmethod
    def convert_type(type_name, obj):
        if type_name in ['str', 'int', 'bool']:
            return eval(f'{type_name}(obj)')
        else:
            return obj
