import argparse
import sys
from types import MappingProxyType
from typing import Iterable

from ._colors import Fore
from ._handler import CommandHandler
from ._command import Command


class Parser(argparse.ArgumentParser):
    prefixes = MappingProxyType(dict(
        usage='usage: ',
        commands='commands',
        url='docs: ',
    ))
    codes = MappingProxyType(dict(
        help=0,
        unknown=1,
        ok=0,
        fail=2,
    ))

    def __init__(self, *, url=None, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self._handlers = dict()

    def _make_command_handler(self, handler, name=None, parser=None) -> CommandHandler:
        if isinstance(handler, CommandHandler):
            if name is not None:
                raise ValueError('cannot re-define name for command')
            if parser is not None:
                raise ValueError('cannot re-define parser for command')
            return handler

        if isinstance(handler, type) and issubclass(handler, CommandHandler):
            return handler(name=name, parser=parser)

        return CommandHandler(name=name, parser=parser, handler=handler)

    def add_command(self, handler, name: str = None,
                    parser: argparse.ArgumentParser = None) -> None:
        handler = self._make_command_handler(
            handler=handler,
            name=name,
            parser=parser,
        )
        self._handlers[handler.name] = handler

    def format_help(self):
        formatter = self._get_formatter()
        prefix = self.prefixes['usage']
        formatter.add_usage(
            usage=self.usage,
            actions=self._actions,
            groups=self._mutually_exclusive_groups,
            prefix=Fore.YELLOW + prefix + Fore.RESET,
        )
        formatter.add_text(self.description)
        if self.url:
            prefix = self.prefixes['url']
            formatter.add_text(Fore.YELLOW + prefix + Fore.RESET + self.url)

        for action_group in self._action_groups:
            formatter.start_section(Fore.YELLOW + action_group.title + Fore.RESET)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
        self._format_commands(formatter=formatter)
        formatter.add_text(self.epilog)
        return formatter.format_help()

    def _get_formatter(self) -> argparse.HelpFormatter:
        formatter = super()._get_formatter()
        formatter._width = 120
        return formatter

    def _format_commands(self, formatter: argparse.HelpFormatter) -> None:
        prefix = self.prefixes['commands']
        formatter.start_section(Fore.YELLOW + prefix + Fore.RESET)
        prev_group = ''
        colors = {True: Fore.GREEN, False: Fore.BLUE}
        color = True
        for name, handler in self._handlers.items():
            # switch colors for every group
            group, _, subname = name.rpartition(' ')
            if group != prev_group:
                prev_group = group
                color = not color

            formatter.add_argument(argparse.Action(
                option_strings=[colors[color] + name + Fore.RESET],
                dest='',
                help=handler.summary,
            ))
        formatter.end_section()

    def get_command(self, argv: Iterable[str] = None) -> CommandHandler:
        if argv is None:
            argv = sys.argv[1:]
        command = Command(argv=argv, commands=self._handlers.keys())
        if not command.match:
            return None
        handler = self._handlers[command.match]
        handler = handler.copy(argv=command.argv)
        return handler

    def handle(self, argv: Iterable[str] = None) -> int:
        if argv is None:
            argv = sys.argv[1:]

        # print help
        if not argv:
            print(self.format_help())
            return self.codes['help']
        if len(argv) == 1 and argv[0] in ('--help', 'help', 'commands'):
            print(self.format_help())
            return self.codes['help']

        # get command
        command = self.get_command(argv=argv)
        if not command:
            print(self.format_help())
            return self.codes['unknown']

        # run command
        result = command()
        if type(result) is bool:
            if result is True:
                return self.codes['ok']
            return self.codes['fail']
        return result
