import json
from lxml.html import fromstring, parse
from .cmd.parser import parse_template
from pathlib import Path
import re


include_statement = re.compile(r'"\s*\$include\(\s*([^()\s]+)\s*\)\s*"')


def from_template(*, template_file=None, template=None, html_file=None, html=None):
    if template_file is not None:
        with open(template_file) as template_reader:
            template = json.load(template_reader)
    elif template is None:
        raise Exception('no template given.')
    if html_file is not None:
        page = parse(html_file)
    elif html is not None:
        page = fromstring(html)
    else:
        raise Exception('empty html.')
    return parse_template(template, page)


def load_template(template_dir, root_template):
    root_template = root_template if isinstance(root_template, Path) else Path(root_template)
    with open(root_template, encoding='utf-8') as root_template_reader:
        template = root_template_reader.read()
    template_dir = template_dir if isinstance(template_dir, Path) else Path(template_dir)
    template = preprocess(template, template_dir)
    return template


def preprocess(template, root_dir):
    for match in include_statement.finditer(template):
        include_file = match.group(1)
        with open(root_dir / f'{include_file}.json', encoding='utf-8') as include_file_reader:
            include_template = include_file_reader.read()
        template = template[:match.start()] + include_template + template[match.end():]
    return json.loads(template)


def from_dir(*, template_dir, root_template, html_file=None, html=None):
    return from_template(template=load_template(template_dir, root_template), html_file=html_file, html=html)
