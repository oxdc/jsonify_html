from ..exceptions import TemplateTypeError, RequiredFieldNotFound, RunTimeError
from ..command_manager import CommandManager
from ..template_manager import TemplateCache
from lxml.html import fromstring, tostring
from datetime import datetime
from dateutil import parser as datetime_parser
from pathlib import Path
import json
import yaml
import re


use_statement = re.compile(r'\$use\(\s*([^()]+)\s*\)')


def parse_use_statement(statement):
    matches = use_statement.findall(statement or '')
    return TemplateCache().get_by_name(matches[0]) if matches else None


def parse_template(template, root):
    if '$cmd' in template:
        try:
            root = CommandManager().run_command_lines(template['$cmd'], root)
        except RunTimeError as e:
            raise
    type_name = template['$type']
    if type_name in ['o', 'obj', 'object']:
        obj = dict()
        for key, value in template.items():
            if not key.startswith('$'):
                if isinstance(value, dict):
                    obj[key] = parse_template(value, root)
                else:
                    obj[key] = value
        return obj
    else:
        return convert_type(type_name, root)


def convert_type(type_name, obj):
    if type_name in ['s', 'str']:
        return str(obj) if obj is not None else ''
    elif type_name in ['i', 'int']:
        return int(obj) if obj is not None else 0
    elif type_name in ['b', 'bool']:
        return bool(obj) if obj is not None else False
    elif type_name in ['datetime', 'date', 'time']:
        return datetime_parser.parse(obj).isoformat() if obj is not None else datetime.fromtimestamp(0).isoformat()
    elif type_name == 'list':
        if obj is None:
            return list()
        return obj if isinstance(obj, list) else list(obj)
    elif type_name == 'set':
        if obj is None:
            return list()
        return list(obj) if isinstance(obj, set) else list(set(obj))
    elif type_name == 'dict':
        if obj is None:
            return dict()
        return obj if isinstance(obj, dict) else dict(obj)
    elif type_name == 'html':
        if obj is None:
            return ''
        elif isinstance(obj, str):
            return tostring(fromstring(obj)).decode('utf-8')
        else:
            return tostring(obj).decode('utf-8')
    else:
        return obj


def load_template(template_file):
    file = Path(template_file)
    if not file.exists():
        raise FileNotFoundError
    if not file.is_file():
        raise IsADirectoryError
    with open(file) as fp:
        if file.suffix == '.json':
            template = json.load(fp)
        elif file.suffix == '.yaml':
            template = yaml.safe_load(fp)
        else:
            raise TypeError("Unsupported template extension")
        return template


def from_template(template, html):
    return parse_template(template, fromstring(html))


class TemplatePackage:
    def __init__(self, main_template=None):
        self.main_template = None
        if main_template is not None:
            self.load_template(main_template)

    def load_template(self, main_template):
        self.main_template = load_template(main_template)
        root_dir = Path(main_template).parent
        for file in root_dir.glob('**/*.*'):
            TemplateCache().register(str(file.relative_to(root_dir)), load_template(file))

    def parse_html(self, html):
        return parse_template(self.main_template, fromstring(html))


def from_package(main_template, html):
    return TemplatePackage(main_template).parse_html(html)


def load_package(main_template):
    return main_template
