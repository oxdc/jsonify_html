import re
from urllib.parse import quote, unquote
from lxml.html.clean import Cleaner
from lxml.html import Element
from lxml.html import tostring, fromstring
from typing import Iterable
from tidylib import tidy_fragment
from lxml.cssselect import CSSSelector


def parse_selector(selector: str):
    if selector.startswith('/') or selector.startswith('./'):
        return selector
    else:
        return CSSSelector(selector).path


def cmd_clean(root, **kwargs):
    return Cleaner(**kwargs).clean_html(root)


def cmd_select(root, selector=None, *, css=None, xpath=None, first=False):
    if selector is not None:
        DOMs = root.xpath(parse_selector(selector))
    elif css is not None:
        DOMs = root.xpath(CSSSelector(css).path)
    elif xpath is not None:
        DOMs = root.xpath(xpath)
    else:
        raise ValueError
    return DOMs[0] if first and DOMs else DOMs


def cmd_text(root):
    return root.text or ""


build_in_commands = {
    "clean": cmd_clean,
    "select": cmd_select,
    "text": cmd_text
}
