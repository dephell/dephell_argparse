import os
import re
import sys
from argparse import ArgumentParser, Namespace
from logging import getLogger
from typing import Optional


REX_WORD = re.compile(r'([a-z\d])([A-Z])')


class CommandHandler:
    logger = getLogger('dephell_argparse')
    parser = None
    name = None

    def __init__(self, *, name=None, parser=None, handler=None, argv=None):
        self.handler = handler
        self.argv = argv

        if name is not None:
            self.name = name
        if self.name is None:
            self.name = self.get_name()

        if parser is not None:
            self.parser = parser
        if self.parser is None:
            self.parser = self.build_parser(parser=self.get_parser())

    def copy(self, **kwargs) -> 'CommandHandler':
        params = vars(self).copy()
        params.update(kwargs)
        return type(self)(**params)

    @property
    def summary(self) -> str:
        return self.parser.description.split('\n')[0]

    @property
    def args(self) -> Namespace:
        return self.parser.parse_args(self.argv)

    def get_name(self) -> str:
        raw = type(self).__name__
        if self.handler is not None:
            raw = self.handler.__name__
        worded = REX_WORD.sub(r'\1 \2', raw)
        normalized = worded.rsplit(' ', maxsplit=1)[0].lower()
        return normalized

    def get_prog(self) -> str:
        return os.path.basename(sys.argv[0])

    def get_parser(self) -> ArgumentParser:
        from ._parser import Parser

        return Parser(
            prog=self.get_prog() + ' ' + self.get_name(),
            usage=self.get_usage(),
            description=self.get_description(),
            url=self.get_url(),
        )

    def get_url(self) -> Optional[str]:
        return None

    def get_usage(self) -> Optional[str]:
        return None

    def get_description(self):
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

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        return parser

    def __call__(self) -> bool:
        if self.handler is not None:
            return self.handler(self.argv)
        raise NotImplementedError
