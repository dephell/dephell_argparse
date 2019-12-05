# built-in
import os
import re
import sys
from argparse import ArgumentParser, Namespace
from inspect import getdoc
from logging import getLogger
from textwrap import dedent
from typing import IO, Iterable, Optional

# app
from ._cached_property import cached_property


REX_WORD = re.compile(r'([a-z\d])([A-Z])')


class CommandHandler:
    logger = getLogger('dephell_argparse')
    stream = sys.stdout
    argv = None

    def __init__(self, *, handler=None, argv: Iterable[str] = None, **kwargs):
        self.__dict__.update()
        self.handler = handler
        if argv is not None:
            self.argv = tuple(argv)

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

    # helpers for handler

    def print(self, *args, sep: str = ' ', end: str = '\n',
              stream: IO = None, flush: bool = False) -> None:
        print(*args, sep=sep, end=end, file=stream or self.stream, flush=flush)

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
        if self.handler is not None:
            raw = self.handler.__name__
            result = raw.split('_')
        else:
            raw = type(self).__name__
            result = REX_WORD.sub(r'\1 \2', raw).split()
        result = [word.strip() for word in result]
        result = [word.lower() for word in result if word]
        if result[-1] == 'handler':
            result = result[:-1]
        if result[-1] == 'command':
            result = result[:-1]
        return ' '.join(result)

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
        doc = self._get_docstring()
        return dedent(doc).strip()

    def _get_docstring(self) -> str:
        doc = getdoc(type(self))
        if doc is not None:
            return doc
        if self.handler is None:
            return ''
        doc = getdoc(self.handler)
        if doc is not None:
            return doc
        return ''

    @cached_property
    def summary(self) -> str:
        return self.parser.description.split('\n')[0]

    @cached_property
    def args(self) -> Namespace:
        return self.parser.parse_args(self.argv)
