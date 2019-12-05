from dephell_argparse import Parser


def hello(args) -> int:
    """Say "hello"!
    """
    print('hello!')
    return 0


parser = Parser()
parser.add_command(hello)


if __name__ == '__main__':
    exit(parser.handle())
