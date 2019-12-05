from dephell_argparse import Parser


def hello(args) -> int:
    print('hello!')
    return 0


parser = Parser()
parser.add_command(hello)


def main() -> int:
    command = parser.get_command()
    if command:
        return command()


if __name__ == '__main__':
    exit(main())
