from .run import CMDRun
from .select_one import CMDSelectOne
from .select import CMDSelect
from .inner_text import CMDInnerText
from .strip import CMDStrip
from .regex import CMDRegex


COMMANDS = {
    'run': CMDRun,
    'select_one': CMDSelectOne,
    'select': CMDSelect,
    'extract_text': CMDInnerText,
    'strip': CMDStrip,
    'regex': CMDRegex
}
