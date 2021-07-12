from lxml.html.clean import Cleaner
from lxml.cssselect import CSSSelector
from .types import Variable
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
def cmd_clean(root, **kwargs):
    return Cleaner(**kwargs).clean_html(root)


@read_only
def cmd_select(root, selector=None, *, css=None, xpath=None, first=False):
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
        DOMs.extend(root.xpath(xpath))
    return DOMs[0] if first and DOMs else DOMs


@read_only
def cmd_remove(root, selector=None, *, css=None, xpath=None, first=False):
    DOMs = cmd_select(root, selector, css=css, xpath=xpath, first=first)
    if first and DOMs:
        remove_preserve_tail(DOMs[0])
    else:
        for DOM in DOMs:
            remove_preserve_tail(DOM)
    return root


@read_only
def cmd_text(root, *, insert_space=True, normalize_spaces=True, ):
    return root.text or ""


build_in_commands = {
    "clean": cmd_clean,
    "select": cmd_select,
    "text": cmd_text
}
