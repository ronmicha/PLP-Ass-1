import os
import sys


def union(*args):
    union_input_validation(args)


def union_input_validation(args):
    if len(args) != 3:
        error_message = "ERROR: Wrong number of arguments. Make sure to pass the following arguments:\n"
        error_message += "<input file 1 path> <input file 2 path> <output file path>"
        raise Exception(error_message)

    input_file_1_extension = os.path.splitext(args[0])[1]
    input_file_2_extension = os.path.splitext(args[1])[1]
    output_file_extension = os.path.splitext(args[2])[1]

    if input_file_1_extension not in (".txt", ".csv") or \
                    input_file_2_extension not in (".txt", ".csv") or \
                    output_file_extension not in (".txt", ".csv"):
        raise Exception("ERROR: Given arguments must be txt or csv files")

    if input_file_1_extension != input_file_2_extension != output_file_extension:
        raise Exception("ERROR: All arguments must be of same type")


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
        action = sys.argv[1].upper()
        if action not in functions_dict:
            raise Exception(action, "is an invalid operation. Valid operations:", ", ".join(functions_dict.keys()))
        functions_dict[action](sys.argv[2:])
    except Exception as ex:
        print ex.message
