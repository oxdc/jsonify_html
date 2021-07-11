import functools


def singleton(cls):
    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance
    wrapper_singleton.instance = None
    return wrapper_singleton


def remove_preserve_tail(element):
    prev = element.getprevious()
    parent = element.getparent()
    if element.tail:
        if prev is not None:
            prev.tail = (prev.tail or '') + element.tail
        else:
            parent.text = (parent.text or '') + element.tail
    parent.remove(element)
