from functools import reduce
from dephell_argparse import Parser, CommandHandler


parser = Parser()


@parser.add_command
class PingCommand(CommandHandler):
    def __call__(self):
        self.print('pong')
        return 0


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
        return 0


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
        return 0


if __name__ == '__main__':
    exit(parser.handle())
