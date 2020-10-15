import json
from lxml.html import fromstring, parse
from .cmd.parser import parse_template
from .cmd.template_manager import cache_template
from pathlib import Path


def from_template(*, template_file=None, template=None, html_file=None, html=None):
    if template_file is not None:
        template_file = template_file if isinstance(template_file, Path) else Path(template_file)
        template = load_template(template_file.parent, template_file)
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
        template = json.load(root_template_reader)
    template_dir = template_dir if isinstance(template_dir, Path) else Path(template_dir)
    templates = {
        str(file.relative_to(template_dir)).replace('\\', '/').replace('.json', '').strip(): file
        for file in template_dir.glob('**/*.json') if file != root_template
    }
    cache_template(templates)
    return template


def from_dir(*, template_dir, root_template, html_file=None, html=None):
    return from_template(template=load_template(template_dir, root_template), html_file=html_file, html=html)
