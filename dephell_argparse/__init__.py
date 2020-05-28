"""Argparse on steroids: groups, commands, colors.
"""

# app
from ._command import Command
from ._handler import CommandHandler
from ._parser import Parser


__version__ = '0.1.3'

__all__ = [
    'Command',
    'CommandHandler',
    'Parser',
]
