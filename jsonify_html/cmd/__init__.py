from .command_manager import CommandManager, register_command
from .implementations.select import CMDSelect
from .implementations.select_one import CMDSelectOne
from .implementations.run import CMDRun
from .implementations.strip import CMDStrip
from .implementations.regex import CMDRegex
from .implementations.inner_text import CMDInnerText
from .implementations.foreach import CMDForEach
from .base import JsonifyCommand

register_command(CMDSelect, name='select')
register_command(CMDSelectOne, name='select_one')
register_command(CMDRun, name='run')
register_command(CMDStrip, name='strip')
register_command(CMDRegex, name='regex')
register_command(CMDInnerText, name='inner_text')
register_command(CMDForEach, name='foreach')
