from ..base import JsonifyCommand
from lxml.html import tostring, fromstring
from tidylib import tidy_fragment


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


class CMDTidy(JsonifyCommand):
    def __init__(self, root, args):
        super().__init__(root)
        self.options = args[0] if len(args) > 0 else dict()
        self.options = {**default_options, **self.options}

    def execute(self):
        return fromstring(tidy_fragment(tostring(self.root), options=self.options)[0])
