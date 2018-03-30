import argparse


def union(args):
    print "union!"


def separate(args):
    print "separate!"


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    sub_parsers = arg_parser.add_subparsers()

    union_parser = sub_parsers.add_parser('UNION')
    union_parser.set_defaults(func=union)

    separate_parser = sub_parsers.add_parser('SEPARATE')
    separate_parser.set_defaults(func=separate)

    args = arg_parser.parse_args()
    args.func(args)
