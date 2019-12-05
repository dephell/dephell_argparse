import os
import re
import sys
from argparse import ArgumentParser, Namespace
from logging import getLogger
from typing import Optional

from ._cached_property import cached_property


REX_WORD = re.compile(r'([a-z\d])([A-Z])')


class CommandHandler:
    logger = getLogger('dephell_argparse')
    parser = None

    def __init__(self, *, handler=None, argv=None, **kwargs):
        self.__dict__.update()
        self.handler = handler
        self.argv = argv

    def copy(self, **kwargs) -> 'CommandHandler':
        params = vars(self).copy()
        params.update(kwargs)
        return type(self)(**params)

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        return parser

    def __call__(self) -> bool:
        if self.handler is not None:
            return self.handler(self.argv)
        raise NotImplementedError

    # defaults

    @cached_property
    def parser(self) -> ArgumentParser:
        from ._parser import Parser

        parser = Parser(
            prog=self.prog + ' ' + self.name,
            usage=self.usage,
            description=self.description,
            url=self.url,
        )
        return self.build_parser(parser=parser)

    @cached_property
    def name(self) -> str:
        raw = type(self).__name__
        if self.handler is not None:
            raw = self.handler.__name__
        worded = REX_WORD.sub(r'\1 \2', raw)
        normalized = worded.rsplit(' ', maxsplit=1)[0].lower()
        return normalized

    @cached_property
    def prog(self) -> str:
        return os.path.basename(sys.argv[0])

    @cached_property
    def url(self) -> Optional[str]:
        return None

    @cached_property
    def usage(self) -> Optional[str]:
        return None

    @cached_property
    def description(self) -> str:
        doc = type(self).__doc__
        if doc is not None:
            return doc
        if self.handler is None:
            return ''
        doc = self.handler.__doc__
        if doc is not None:
            return doc
        doc = type(self.handler).__doc__
        if doc is not None:
            return doc
        return ''

    @cached_property
    def summary(self) -> str:
        return self.parser.description.split('\n')[0]

    @cached_property
    def args(self) -> Namespace:
        return self.parser.parse_args(self.argv)
