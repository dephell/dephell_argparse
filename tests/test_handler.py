# external
import pytest

# project
from dephell_argparse import CommandHandler


@pytest.mark.parametrize('given, expected', [
    ('hello', 'hello'),
    ('Hello', 'hello'),
    ('HelloCommand', 'hello'),
    ('MathSum', 'math sum'),
    ('MathSumCommand', 'math sum'),
    ('MathSumHandler', 'math sum'),
    ('MathSumCommandHandler', 'math sum'),
    ('MathCommand', 'math'),
    ('URL', 'url'),
    ('ParseURL', 'parse url'),
    ('URLParse', 'urlparse'),
])
def test_name_class(given: str, expected: str):
    cls = type(given, (CommandHandler, ), {})
    assert cls().name == expected


@pytest.mark.parametrize('given, expected', [
    ('hello', 'hello'),
    ('math_sum', 'math sum'),
    ('math_sum_command', 'math sum'),
])
def test_name_func(given: str, expected: str):
    cls = type(given, (), {})
    assert CommandHandler(handler=cls).name == expected


def test_description():
    def handler():
        """test me!
        """

    assert CommandHandler(handler=handler).description == 'test me!'

    class Handler(CommandHandler):
        """test me!
        """

    assert Handler().description == 'test me!'

    class Handler:
        """test me!
        """

    assert CommandHandler(handler=Handler()).description == 'test me!'
