# built-in
from functools import reduce

# project
from dephell_argparse import CommandHandler, Parser


parser = Parser()


@parser.add_command
class PingCommand(CommandHandler):
    def __call__(self):
        self.print('pong')
        return 14


@parser.add_command
class MathSumCommand(CommandHandler):
    """Return sum of numbers
    """
    @staticmethod
    def build_parser(parser: Parser) -> Parser:
        parser.add_argument('numbers', type=int, nargs='+')
        return parser

    def __call__(self):
        result = sum(self.args.numbers)
        self.print(result)
        return 15


@parser.add_command
class MathProdCommand(CommandHandler):
    """Return product of numbers
    """
    @staticmethod
    def build_parser(parser: Parser) -> Parser:
        parser.add_argument('numbers', type=int, nargs='+')
        return parser

    def __call__(self):
        result = reduce(lambda a, b: a * b, self.args.numbers)
        self.print(result)
        return 16


def test_handle():
    assert parser.handle(argv=[]) == 0
    assert parser.handle(argv=['help']) == 0
    assert parser.handle(argv=['--help']) == 0
    assert parser.handle(argv=['math']) == 1
    assert parser.handle(argv=['ping']) == 14
    assert parser.handle(argv=['math', 'sum', '1', '2']) == 15
