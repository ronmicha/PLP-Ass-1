import os
import sys
import re
from ast import literal_eval

delimiters = r":|::"


def union(*args):
    args = args[0]  # Extract arguments list from *args tuple
    input_validation(args, is_union=True)
    tables_structure_validation(args[0], args[1])
    with open(args[2], "w") as output_file:
        for input_file_path in [args[0], args[1]]:
            file_name = os.path.basename(input_file_path)
            with open(input_file_path, "r") as input_file:
                for row in input_file:
                    output_file.write("{0}:{1}\n".format(row.strip(), file_name))


def separate(*args):
    args = args[0]  # Extract arguments list from *args tuple
    input_validation(args, is_union=False)
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


def input_validation(args, is_union):
    if len(args) != 3:
        raise Exception("ERROR: Wrong number of arguments. This operation requires 3 arguments")

    if not os.path.isfile(args[0]) or (is_union and not os.path.isfile(args[1])):
        raise Exception("ERROR: Input arguments don't exist")

    arg_1_extension = os.path.splitext(args[0])[1]
    arg_2_extension = os.path.splitext(args[1])[1]
    arg_3_extension = os.path.splitext(args[2])[1]

    if arg_1_extension not in (".txt", ".csv") or \
                    arg_2_extension not in (".txt", ".csv") or \
                    arg_3_extension not in (".txt", ".csv"):
        raise Exception("ERROR: Given arguments must be txt or csv files")

    if arg_1_extension != arg_2_extension != arg_3_extension:
        raise Exception("ERROR: All arguments must be of same type")


def tables_structure_validation(input_file_1_path, input_file_2_path):
    with open(input_file_1_path, "r") as f:
        first_line_1 = f.readline()
    with open(input_file_2_path, "r") as f:
        first_line_2 = f.readline()
    split_line_1 = re.split(delimiters, first_line_1)
    split_line_2 = re.split(delimiters, first_line_2)
    if len(split_line_1) != len(split_line_2):  # Different number of columns
        raise Exception("ERROR: The tables' format does not match")
        # TODO: compare types of each column


if __name__ == "__main__":
    try:
        functions_dict = \
            {
                "UNION": union,
                "SEPARATE": separate,
                "DISTINCT": distinct,
                "LIKE": like
            }
        action = sys.argv[1].upper()
        if action not in functions_dict:
            raise Exception("Invalid operation {0}. Valid operations: {1}".format(action, ", ".join(functions_dict.keys())))
        functions_dict[action](sys.argv[2:])
    except Exception as ex:
        print ex.message
