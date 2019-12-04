import argparse
from types import MappingProxyType

from ._colors import Fore
from ._handler import CommandHandler


class Parser(argparse.ArgumentParser):
    prefixes = MappingProxyType(dict(
        usage='usage: ',
        commands='commands:',
    ))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._handlers = []

    def _make_command_handler(self, handler, name=None, parser=None) -> CommandHandler:
        if isinstance(handler, CommandHandler):
            if name is not None:
                raise ValueError('cannot re-define name for command')
            if parser is not None:
                raise ValueError('cannot re-define parser for command')
            return handler

        if issubclass(handler, CommandHandler):
            return handler(name=name, parser=parser)

        if name is None:
            raise ValueError('name required')
        if parser is None:
            raise ValueError('parser required')
        return CommandHandler(name=name, parser=parser, handler=handler)

    def add_command(self, handler, name: str = None,
                    parser: argparse.ArgumentParser = None) -> None:
        self._handlers.append(self._make_command_handler(
            handler=handler,
            name=name,
            parser=parser,
        ))

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

        for action_group in self._action_groups:
            # do not show comma-separated commands list
            if action_group.title == 'positional arguments':
                continue
            formatter.start_section(Fore.YELLOW + action_group.title + Fore.RESET)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()
        formatter.add_text(self.epilog)
        self._format_commands(formatter=formatter)
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
        for handler in self._handlers:
            # switch colors for every group
            group, _, subname = handler.name.rpartition(' ')
            if group != prev_group:
                prev_group = group
                color = not color

            formatter.add_argument(argparse.Action(
                option_strings=[colors[color] + handler.name + Fore.RESET],
                dest='',
                help=handler.summary,
            ))
        formatter.end_section()
