# external
import pytest

# project
from dephell_argparse._command import Command


def test_groups():
    commands = ('math sum', 'math prod', 'http get', 'hello')
    groups = ('math', 'http')
    assert Command(argv=[], commands=commands).groups == frozenset(groups)


@pytest.mark.parametrize('left, right, result', [
    ('twilight', 'twilight', True),
    ('twilight', 'twiligth', True),
    ('twilight', 'twiight', True),
    ('twilight', 'sparkle', False),
    ('twilight', 'ghttw', False),
])
def test_similar(left, right, result):
    assert Command._similar(left, right) == result


TEST_COMMANDS = (
    'math prod',
    'math sum',
    'http get',
    'http post',
    'http patch',
    'http delete',
    'do something',
    'auth',
    'hello',
    'hello there',
    'bye there',
)


@pytest.mark.parametrize('argv, match', [
    # full match
    (['math', 'prod'], 'math prod'),
    (['math', 'prod', 'some', 'junk'], 'math prod'),

    # args don't affect
    (['junk', 'math', 'prod'], None),
    (['math', '--prod'], None),

    #  partial match
    (['prod'], 'math prod'),
    (['prod', 'junk'], 'math prod'),
    (['do'], 'do something'),
    (['something'], 'do something'),
    (['something', 'else'], 'do something'),
    (['do', 'else'], 'do something'),

    (['hello'], 'hello'),
    (['hello', 'there'], 'hello there'),
    (['hello', 'not', 'there'], 'hello'),

    (['math'], None),
    (['there'], None),
])
def test_match(argv, match):
    cmd = Command(argv=argv, commands=TEST_COMMANDS)
    assert cmd.match == match
