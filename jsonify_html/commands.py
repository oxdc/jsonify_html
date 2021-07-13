import re

from lxml.html.clean import Cleaner
from lxml.cssselect import CSSSelector
from .types import *
import functools


def read_only(func):
    @functools.wraps(func)
    def wrapper_read_only(*args, **kwargs):
        _args = [arg.value if isinstance(arg, Variable) else arg for arg in args]
        _kwargs = {key: arg.value if isinstance(arg, Variable) else arg for key, arg in kwargs.items()}
        return func(*_args, **_kwargs)
    return wrapper_read_only


def parse_selector(selector: str):
    if selector.startswith('/') or selector.startswith('./'):
        return selector
    else:
        return CSSSelector(selector).path


def remove_preserve_tail(element):
    prev = element.getprevious()
    parent = element.getparent()
    if element.tail:
        if prev is not None:
            prev.tail = (prev.tail or '') + element.tail
        else:
            parent.text = (parent.text or '') + element.tail
    parent.remove(element)


@read_only
def cmd_clean(node, **kwargs):
    return Cleaner(**kwargs).clean_html(node.root)


@read_only
def cmd_select(node, selector=None, *, css=None, xpath=None, first=False):
    if selector is not None:
        selectors = selector if isinstance(selector, list) else [selector]
        xpaths = map(parse_selector, selectors)
    elif css is not None:
        selectors = css if isinstance(css, list) else [css]
        xpaths = map(lambda c: CSSSelector(c).path, selectors)
    elif xpath is not None:
        xpaths = xpath if isinstance(xpath, list) else [xpath]
    else:
        raise ValueError
    DOMs = []
    for xpath in xpaths:
        DOMs.extend(node.root.xpath(xpath))
    return DOMs[0] if first and DOMs else DOMs


@read_only
def cmd_remove(node, selector=None, *, css=None, xpath=None, first=False):
    DOMs = cmd_select(node.root, selector, css=css, xpath=xpath, first=first)
    if first and DOMs:
        remove_preserve_tail(DOMs[0])
    else:
        for DOM in DOMs:
            remove_preserve_tail(DOM)
    return node.root


@read_only
def cmd_text(node, *, insert_space=True, normalize_spaces=True, ):
    return node.root.text or ""


def cmd_eval(node, expr):
    if isinstance(expr, Function):
        return expr(node)
    elif isinstance(expr, Variable):
        return expr.value
    elif isinstance(expr, str):
        _expr = expr
        for var in re.findall(r"\$[a-zA-Z0-9_]+", expr):
            _var = node.get_variable(Ref(name=var.strip('$')))
            _expr = _expr.replace(var, str(_var.value) if _var is not None else "None")
        return eval(_expr)
    else:
        return node.root


def cmd_exec(node, expr):
    if isinstance(expr, Function):
        expr(node)
    elif isinstance(expr, str):
        _expr = expr
        for var in re.findall(r"\$[a-zA-Z0-9_]+", expr):
            _var = node.get_variable(Ref(name=var.strip('$')))
            _expr = _expr.replace(var, str(_var.value) if _var is not None else "None")
        exec(_expr)
    return node.root


def cmd_print(node, *args, **kwargs):
    print(*args, **kwargs)
    return node.root


def cmd_set(node, variable, value):
    assert isinstance(variable, Variable)
    if isinstance(value, Function):
        variable.value = value(node)
    else:
        variable.value = value
    return node.root


def cmd_foreach(node, func):
    assert isinstance(func, Function)
    argc = len(func.arg_names)
    root = []
    for i, item in enumerate(node.root):
        node.root = item
        if argc == 0:
            result = func(node)
        elif argc == 1:
            result = func(node, item)
        elif argc == 2:
            result = func(node, i, item)
        else:
            result = func(node)
        root.append(result)
    node.root = root
    return root


def cmd_apply(node, root, template):
    template.value.root = root
    template.value.update_variables(node.variables)
    template.value.update_methods(node.methods)
    node.root = template.value.execute()
    return node.root


build_in_commands = {
    "clean": cmd_clean,
    "select": cmd_select,
    "text": cmd_text,
    "eval": cmd_eval,
    "exec": cmd_exec,
    "print": cmd_print,
    "set": cmd_set,
    "foreach": cmd_foreach,
    "apply": cmd_apply
}
