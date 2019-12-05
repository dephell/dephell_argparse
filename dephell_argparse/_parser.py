# built-in
import argparse
import sys
from types import MappingProxyType
from typing import IO, Dict, Optional, Sequence

# app
from ._colors import Fore
from ._command import Command
from ._handler import CommandHandler


class Parser(argparse.ArgumentParser):
    prefixes = MappingProxyType(dict(
        usage='USAGE: ',
        commands='COMMANDS',
        group='COMMANDS IN GROUP',
        guesses='POSSIBLE COMMANDS',
        url='DOCS: ',
        description='DESCRIPTION: ',
    ))
    codes = MappingProxyType(dict(
        help=0,
        unknown=1,
        ok=0,
        fail=2,
    ))

    def __init__(self, *, url: str = None, stream: IO = sys.stderr, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.stream = stream
        self._handlers = dict()  # type: Dict[str, CommandHandler]

    def _print_message(self, message: str, file: IO = None) -> None:
        if not message:
            return
        if file is None:
            file = self.stream
        file.write(message)

    def _make_command_handler(self, handler, name: str = None,
                              parser: argparse.ArgumentParser = None) -> CommandHandler:
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

    def format_help(self, command: Command = None):
        formatter = self._get_formatter()
        colorize = (Fore.YELLOW + '{}' + Fore.RESET).format

        if self.usage:
            formatter.add_usage(
                usage=self.usage,
                actions=self._actions,
                groups=self._mutually_exclusive_groups,
                prefix=colorize(self.prefixes['usage']),
            )

        if command and not command.match and not command.group:
            msg = '{}ERROR:{} command not found'
            formatter.add_text(msg.format(Fore.RED, Fore.RESET))

        if self.description:
            formatter.add_text(colorize(self.prefixes['description']) + self.description)
        if self.url:
            formatter.add_text(colorize(self.prefixes['url']) + self.url)

        for action_group in self._action_groups:
            title = action_group.title or ''
            formatter.start_section(colorize(title.upper()))
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
        self._format_commands(formatter=formatter, command=command)
        formatter.add_text(self.epilog)
        return formatter.format_help()

    def _get_formatter(self) -> argparse.HelpFormatter:
        formatter = super()._get_formatter()
        formatter._width = 120
        return formatter

    def _format_commands(self, formatter: argparse.HelpFormatter,
                         command: Command = None) -> None:
        prefix = self.prefixes['commands']
        if command:
            if command.group:
                prefix = self.prefixes['group']
            elif command.guesses:
                prefix = self.prefixes['guesses']

        formatter.start_section(Fore.YELLOW + prefix + Fore.RESET)
        prev_group = ''
        colors = {True: Fore.GREEN, False: Fore.BLUE}
        color = True
        for name, handler in self._handlers.items():
            if command and command.guesses and name not in command.guesses:
                continue
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

    def get_command(self, argv: Sequence[str] = None) -> Optional[CommandHandler]:
        if argv is None:
            argv = sys.argv[1:]
        command = Command(argv=argv, commands=self._handlers.keys())
        if not command.match:
            return None
        handler = self._handlers[command.match]
        handler = handler.copy(argv=command.argv)
        return handler

    def handle(self, argv: Sequence[str] = None) -> int:
        if argv is None:
            argv = sys.argv[1:]

        # print help
        if not argv:
            self._print_message(self.format_help())
            return self.codes['help']
        if len(argv) == 1 and argv[0] in ('--help', 'help', 'commands'):
            self._print_message(self.format_help())
            return self.codes['help']

        # rewrite command to get help about command
        if len(argv) >= 1 and argv[0] in ('--help', 'help'):
            argv = list(argv[1:]) + ['--help']

        # get command
        handler = self.get_command(argv=argv)
        if not handler:
            command = Command(argv=argv, commands=self._handlers.keys())
            self._print_message(self.format_help(command=command))
            return self.codes['unknown']

        # run command
        result = handler()
        if type(result) is bool:
            if result is True:
                return self.codes['ok']
            return self.codes['fail']
        return result
