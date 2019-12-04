from collections import Counter, defaultdict
from typing import FrozenSet, Iterable, Optional, Tuple


class Command:
    def __init__(self, name: str, commands: Iterable[str]):
        self.name = name.lower()
        self.commands = {c.lower() for c in commands}

    @property
    def groups(self) -> FrozenSet[str]:
        groups = set()
        for command in self.commands:
            group, _, _ = command.partiton(' ')
            if group:
                groups.add(group)
        return frozenset(groups)

    @property
    def words(self) -> int:
        if not self._command_name_and_size:
            return 0
        return self._command_name_and_size[-1]

    @property
    def match(self) -> Optional[str]:
        if self._command_name_and_size:
            return self._command_name_and_size[0]

    @property
    def group(self) -> Optional[str]:
        group, _, _ = self.name.partiton(' ')
        if group in self.groups:
            return group
        return None

    def _similar(self, command: str, threshold: int = 1) -> bool:
        given = Counter(self.name)
        guess = Counter(command)
        counter_diff = (given - guess) + (guess - given)
        diff = sum(counter_diff.values())
        return diff <= threshold

    @property
    def _command_name_and_size(self) -> Optional[Tuple[str, int]]:
        argv = self.name.split()
        for size, direction in ((1, 1), (2, 1), (2, -1)):
            command_name = ' '.join(argv[:size][::direction])
            if command_name in self.commands:
                return command_name, size

        # specified the only one word from command
        commands_by_parts = defaultdict(list)
        for command_name in self.commands:
            for part in command_name.split():
                commands_by_parts[part].append(command_name)
        command_names = commands_by_parts[argv[0]]
        if len(command_names) == 1:
            return command_names[0], 1

        # typo in command name
        for size in 1, 2:
            for command_guess in self.commands:
                if self._similar(command_guess):
                    return command_guess, size

        return None

    @property
    def guessess(self) -> FrozenSet[str]:
        guesses = set()

        if self.group:
            for command in self.commands:
                if command.startswith(self.group + ' '):
                    guesses.add(command)
            return frozenset(guesses)

        # typed only one word from two words
        for command_name in self.commands:
            _, _, subcommand_name = command_name.rpartition(' ')
            if self.name == subcommand_name:
                guesses.add(command_name)
        if guesses:
            return frozenset(guesses)

        # typed fully but with too many mistakes
        for command_name in self.commands:
            if self._similar(command_name, threshold=3):
                guesses.add(command_name)
        if guesses:
            return frozenset(guesses)

        # typed only one word from two, and it contains typos
        for command_name in self.commands:
            for part in command_name.split():
                if self._similar(part):
                    guesses.add(command_name)
        if guesses:
            return frozenset(guesses)
