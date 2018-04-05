import os
import sys
import re

delimiter = r"::"


def union(*args):
    args = args[0]  # Extract arguments list from *args tuple
    input_validation(args, is_union=True)
    tables_structure_validation(args[0], args[1])
    with open(args[2], "w") as output_file:
        for input_file_path in [args[0], args[1]]:
            file_name = os.path.basename(input_file_path)
            with open(input_file_path, "r") as input_file:
                for line in input_file:
                    line = line.strip()
                    # ToDo (overkill): if the files have the same base file name, then it won't be a unique value
                    output_file.write("{0}{1}{2}\n".format(line, delimiter, file_name))


def separate(*args):
    args = args[0]  # Extract arguments list from *args tuple
    input_validation(args, is_union=False)
    identifier_to_file = {}
    current_file = 0
    with open(args[1], "w") as output_file_1:
        with open(args[2], "w") as output_file_2:
            files = {0: output_file_1, 1: output_file_2}
            with open(args[0], "r") as input_file:
                for line in input_file:
                    split_line = re.split(delimiter, line)
                    identifier = split_line[-1].rstrip()  # remove /n
                    if identifier not in identifier_to_file.keys():
                        assert current_file <= 1, 'Found more than two distinct file identifiers: {0},{1}'.format(
                            ",".join(identifier_to_file.keys()), identifier)
                        identifier_to_file[identifier] = files[current_file]
                        current_file += 1
                    new_line = delimiter.join(split_line[:-1]) + "\n"
                    identifier_to_file[identifier].write(new_line)


def distinct(*args):
    input_file_path = args[0]
    column_index = args[1]
    output_file_path = args[2]


def like(*args):
    input_file_path = args[0]
    column_index = args[1]
    regex = args[2]


def input_validation(args, is_union):
    assert len(args) == 3, "Wrong number of arguments. This operation requires 3 arguments"

    assert os.path.isfile(args[0]) and (not is_union or os.path.isfile(args[1])), "Input arguments don't exist"

    args_extensions = [os.path.splitext(arg)[1] for arg in args]

    for arg_extension in args_extensions:
        assert arg_extension in (".txt", ".csv"), "All arguments must be txt or csv files"

    assert args_extensions.count(args_extensions[0]) == len(args_extensions), "All arguments must be of same type"


def tables_structure_validation(file_1_path, file_2_path):
    import numpy as np
    from string import digits
    # https://penandpants.com/2012/03/09/reading-text-tables-with-python/

    file_1_structure = np.genfromtxt(file_1_path, delimiter=delimiter, dtype=None).dtype
    file_2_structure = np.genfromtxt(file_2_path, delimiter=delimiter, dtype=None).dtype
    error_message = "The tables' format does not match"

    assert len(file_1_structure) == len(file_2_structure), error_message

    for i in range(len(file_1_structure.fields)):
        # Extract dtype name of column i and remove digits from it (so that 'int64' == 'int32')
        file_1_col_i_type = file_1_structure.fields.values()[i][0].name.translate(None, digits)
        file_2_col_i_type = file_2_structure.fields.values()[i][0].name.translate(None, digits)
        assert file_1_col_i_type == file_2_col_i_type, error_message


if __name__ == "__main__":
    try:
        functions_dict = \
            {
                "UNION": union,
                "SEPARATE": separate,
                "DISTINCT": distinct,
                "LIKE": like
            }
        # ToDo: in his examples it says seperate

        assert len(sys.argv) >= 2, "Missing operation. Available operations: {0}".format(
            ", ".join(functions_dict.keys()))

        action = sys.argv[1].upper()

        assert action in functions_dict, "Invalid operation {0}. Valid operations: {1}".format(action, ", ".join(
            functions_dict.keys()))

        functions_dict[action](sys.argv[2:])

    except Exception as ex:
        print "ERROR:", ex.message
