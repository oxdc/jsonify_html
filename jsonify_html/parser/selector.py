from lxml.cssselect import CSSSelector


def parse_selector(selector: str):
    if selector.startswith('/') or selector.startswith('./'):
        return selector
    else:
        return CSSSelector(selector).path
