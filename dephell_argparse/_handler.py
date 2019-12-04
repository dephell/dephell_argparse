import re
from argparse import ArgumentParser
from logging import getLogger


REX_WORD = re.compile(r'([a-z\d])([A-Z])')


class CommandHandler:
    logger = getLogger('dephell_argparse')
    parser = None

    def __init__(self, *, name=None, parser=None, handler=None):
        if parser is not None:
            self.parser = parser
        if self.parser is None:
            self.parser = self.build_parser(parser=self.get_parser())

        if name is not None:
            self.name = name
        if self.name is None:
            self.name = self.get_name()

        self.handler = handler

    @property
    def summary(self) -> str:
        return self.parser.description.split('\n')[0]

    @classmethod
    def get_name(cls):
        worded = REX_WORD.sub(r'\1 \2', cls.__name__)
        return worded.rsplit(' ', maxsplit=1)[0].lower()

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        name = cls._get_name()
        url = 'https://dephell.org/docs/cmd-{}.html'.format(name.replace(' ', '-'))
        usage = ''
        usage = 'dephell {} [OPTIONS] {}'.format(name, usage.upper())
        return ArgumentParser(
            prog='dephell ' + name,
            usage=usage + '\n\n\ndocs: ' + url,
            description=cls.__doc__,
            epilog=url,
        )

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        raise NotImplementedError

    def __call__(self) -> bool:
        if self.handler is not None:
            return self.handler()
        raise NotImplementedError
