import re
from argparse import ArgumentParser
from logging import getLogger


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

    def get_name(self) -> str:
        raw = type(self).__name__
        if self.handler is not None:
            raw = self.handler.__name__
        worded = REX_WORD.sub(r'\1 \2', raw)
        normalized = worded.rsplit(' ', maxsplit=1)[0].lower()
        return normalized

    def get_parser(self) -> ArgumentParser:
        name = self.get_name()
        url = 'https://dephell.org/docs/cmd-{}.html'.format(name.replace(' ', '-'))
        usage = ''
        usage = 'dephell {} [OPTIONS] {}'.format(name, usage.upper())
        return ArgumentParser(
            prog='dephell ' + name,
            usage=usage + '\n\n\ndocs: ' + url,
            description=type(self).__doc__,
            epilog=url,
        )

    @classmethod
    def build_parser(cls, parser: ArgumentParser) -> ArgumentParser:
        return parser

    def __call__(self) -> bool:
        if self.handler is not None:
            return self.handler(self.argv)
        raise NotImplementedError
