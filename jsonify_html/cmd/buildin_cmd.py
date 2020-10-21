import re
from urllib.parse import quote, unquote
from lxml.html.clean import Cleaner
from lxml.html import Element
from lxml.html import tostring, fromstring
from typing import Iterable
from tidylib import tidy_fragment
from ..parser.template import parse_template, parse_use_statement
from ..parser.selector import parse_selector
from ..command_manager import register_command, CommandManager
from ..template_manager import TemplateCache
from ..utils import remove_preserve_tail


@register_command('recursive')
def cmd_recursive(root):
    results = []
    for el in root.xpath('./*'):
        templates = TemplateCache().get_by_match(el)
        for template in templates:
            data = parse_template(template, el)
            if data is not None:
                results.append(data)
        if templates:
            remove_preserve_tail(el)
    return results


@register_command('foreach')
def cmd_foreach(root, *args, template=None):
    if template is None and args:
        return [CommandManager().run_command_line(args, child) for child in root]
    if isinstance(template, str):
        template = parse_use_statement(template)
    return [parse_template(template, child) for child in root]


@register_command('clean')
def cmd_clean(root, **kwargs):
    return Cleaner(**kwargs).clean_html(root)


@register_command('concat_list')
def cmd_concat_list(root, recursive=False):
    result = []
    for item in root:
        if not isinstance(item, Iterable):
            result.append(item)
        elif recursive:
            result.extend(cmd_concat_list(item, True))
        else:
            result.extend(item)
    return result


@register_command('delete_attrib')
def cmd_delete_attribute(root, selector, *args):
    xpath = parse_selector(selector)
    for el in root.xpath(xpath):
        for attr in args:
            if attr in el.attrib:
                del el.attrib[attr]
    return root


@register_command('minify')
def cmd_minify(root, line_break=True, tab=True, quoted=True):
    multiple_spaces = re.compile(r'\s\s+')
    html = tostring(root).decode('utf-8')
    if line_break:
        html = html.replace('\n', '')
    if tab:
        html = html.replace('\t', '')
    if quoted:
        for char in ['&#09;', '&#10;', '&#13;', '&#160;']:
            html = html.replace(char, '')
    html = multiple_spaces.sub(' ', html)
    return fromstring(html)


@register_command('strip')
def cmd_strip(root):
    return root.strip()


@register_command('split')
def cmd_split(root, char=None):
    return root.split(char)


@register_command('quote')
def cmd_quote(root):
    return quote(root)


@register_command('unquote')
def cmd_unquote(root):
    return unquote(root)


@register_command('text')
def cmd_text(root):
    return root.text or ''


@register_command('tail')
def cmd_tail(root):
    return root.tail


@register_command('regex')
def cmd_regex(root, pattern, action, *args):
    regex = re.compile(pattern)
    string = root if isinstance(root, str) else tostring(root).decode('utf-8')
    if action == 'get':
        matches = regex.findall(string)
        if len(args) == 1:
            return matches[args[0]] if len(matches) > args[0] else None
        elif len(args) > 1:
            results = []
            for arg in args:
                if len(matches) > arg:
                    results.append(matches[arg])
            return results
        else:
            return matches
    elif action == 'replace':
        return regex.sub(args[0], string)
    elif action == 'split':
        return regex.split(string)
    else:
        return root


@register_command('remove')
def cmd_remove(root, *args):
    for selector in args:
        xpath = parse_selector(selector)
        for el in root.xpath(xpath):
            remove_preserve_tail(el)
    return root


@register_command('eval')
def cmd_eval(root, statement):
    return eval(statement.replace('$root', 'root'))


@register_command('exec')
def cmd_exec(root, source):
    exec(source.replace('$root', 'root'))
    return root


@register_command('select')
def cmd_select(root, selector):
    xpath = parse_selector(selector)
    return root.xpath(xpath)


@register_command('select_one')
def cmd_select_one(root, selector):
    results = cmd_select(root, selector)
    return results[0] if len(results) else None


@register_command('select_or')
def cmd_select_or(root, *selectors):
    selectors = [parse_selector(selector) for selector in selectors]
    selector = ' | '.join(selectors)
    return root.xpath(selector)


@register_command('select_one_or')
def cmd_select_or(root, *selectors):
    results = cmd_select_or(root, selectors)
    return results[0] if len(results) else None


@register_command('tidy')
def cmd_tidy(root, **kwargs):
    default_options = {
        'clean': 0,
        'drop-empty-elements': 0,
        'drop-empty-paras': 0,
        'drop-proprietary-attributes': 1,
        'logical-emphasis': 0,
        'merge-divs': 0,
        'merge-spans': 0,
        'anchor-as-name': 1,
        'coerce-endtags': 1,
        'custom-tags': 'blocklevel',
        'enclose-block-text': 0,
        'enclose-text': 0,
        'escape-scripts': 1,
        'fix-backslash': 1,
        'fix-style-tags': 1,
        'fix-uri': 1,
        'literal-attributes': 0,
        'uppercase-attributes': 0,
        'uppercase-tags': 0,
        'hide-comments': 1,
        'join-classes': 1,
        'join-styles': 1,
        'merge-emphasis': 0,
        'replace-color': 0,
        'break-before-br': 0,
        'indent': 0,
        'indent-attributes': 0,
        'keep-tabs': 0,
        'omit-optional-tags': 0,
        'tidy-mark': 0,
        'vertical-space': 0
    }
    options = {**default_options, **kwargs}
    return fromstring(tidy_fragment(tostring(root), options=options)[0])


@register_command('wrap')
def cmd_wrap(root, tag, **kwargs):
    parent = Element(tag, **kwargs)
    parent.insert(0, root)
    return parent


@register_command('copy')
def cmd_copy(root):
    return fromstring(tostring(root))


@register_command('inner_text')
def cmd_inner_text(root):
    return root.xpath('string()')


@register_command('inner_html')
def cmd_inner_html(root):
    outer_html = tostring(root)
    inner_html = outer_html[outer_html.find(b'>') + 1:outer_html.rfind(b'<')]
    return fromstring(inner_html) if inner_html else '<p></p>'


@register_command('parse_html')
def cmd_parse_html(root):
    return fromstring(root)
