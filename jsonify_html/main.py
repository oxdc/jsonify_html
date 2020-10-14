import json
from lxml.html import fromstring, parse
from .cmd.parser import parse_template


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
