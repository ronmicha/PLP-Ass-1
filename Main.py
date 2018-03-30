import sys


def union(*args):
    input_file_path_1 = args[0]
    input_file_path_2 = args[1]
    output_file_path = args[2]


def separate(*args):
    input_file_path = args[0]
    output_file_path_1 = args[1]
    output_file_path_2 = args[2]


def distinct(*args):
    input_file_path = args[0]
    column_index = args[1]
    output_file_path = args[2]


def like(*args):
    input_file_path = args[0]
    column_index = args[1]
    regex = args[2]


if __name__ == "__main__":
    functions_dict = \
        {
            "UNION": union,
            "SEPARATE": separate,
            "DISTINCT": distinct,
            "LIKE": like
        }
    try:
        action = sys.argv[1]
        functions_dict[action](sys.argv[2:])
    except Exception as ex:
        print ex.message
