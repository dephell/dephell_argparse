from dephell_argparse import Parser, CommandHandler


class SumCommand(CommandHandler):
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


parser = Parser()
parser.add_command(SumCommand)


if __name__ == '__main__':
    exit(parser.handle())
