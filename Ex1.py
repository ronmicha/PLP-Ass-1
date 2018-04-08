import os
import sys
import re

delimiter = r"::"


def string_to_var(value):
    assert value, "Problem parsing value"
    try:
        return eval(value)
    except Exception:
        return value


def union(*args):
    args = args[0]  # Extract arguments list from *args tuple
    union_separate_input_validation(args, is_union=True)
    tables_structure_validation(args[0], args[1])
    unique_val = 0
    with open(args[2], "w") as output_file:
        unique_val += 1
        for input_file_path in [args[0], args[1]]:
            with open(input_file_path, "r") as input_file:
                for line in input_file:
                    line = line.strip()
                    output_file.write("{0}{1}{2}\n".format(line, delimiter, unique_val))


def separate(*args):
    args = args[0]  # Extract arguments list from *args tuple
    union_separate_input_validation(args, is_union=False)
    identifier_to_file = {}
    current_file = 0
    with open(args[1], "w") as output_file_1:
        with open(args[2], "w") as output_file_2:
            files = {0: output_file_1, 1: output_file_2}
            with open(args[0], "r") as input_file:
                for line in input_file:
                    split_line = re.split(delimiter, line)
                    identifier = split_line[-1].rstrip()  # remove /n
                    if identifier not in identifier_to_file:
                        assert current_file <= 1, 'Found more than two distinct file identifiers: {0},{1}'.format(
                            ",".join(identifier_to_file.keys()), identifier)
                        identifier_to_file[identifier] = files[current_file]
                        current_file += 1
                    new_line = delimiter.join(split_line[:-1]) + "\n"
                    identifier_to_file[identifier].write(new_line)


def union_separate_input_validation(args, is_union):
    assert len(args) == 3, "Wrong number of arguments. This operation requires 3 arguments"

    assert os.path.isfile(args[0]) and (not is_union or os.path.isfile(args[1])), "Input arguments don't exist"

    args_extensions = [os.path.splitext(arg)[1] for arg in args]

    for arg_extension in args_extensions:
        assert arg_extension in (".txt", ".csv"), "All arguments must be txt or csv files"

    assert args_extensions.count(args_extensions[0]) == len(args_extensions), "All arguments must be of same type"


# region Distinct

def distinct(*args):
    args = args[0]
    distinct_input_validation(args)
    input_file_path = args[0]
    column_index = int(args[1])
    output_file_path = args[2]
    result_set = []  # Using list instead of set because set is not ordered
    with open(input_file_path, "r") as input_file:
        for line in input_file:
            value = string_to_var(re.split(delimiter, line)[column_index].rstrip())
            if value not in result_set:
                result_set.append(value)

    result_set = sort_with_type(result_set)
    with open(output_file_path, "w") as output_file:
        for val in result_set:
            output_file.write(str(val) + '\n')


def sort_with_type(result_set):
    first_val = next(iter(result_set))
    # For numbers, sort normally:
    if isinstance(type(first_val), int):
        return sorted(result_set)
    # For strings, sort with no case:
    if isinstance(first_val, basestring):
        return sorted(result_set, key=lambda v: (v.upper(), v[0].islower()))
    # For lists, don't sort:
    return result_set


def distinct_input_validation(args):
    assert len(args) == 3, "Wrong number of arguments. This operation requires 3 arguments"
    assert os.path.isfile(args[0]), "Input file does not exist"
    assert isinstance(type(string_to_var(args[1])), int) and int(args[1]) >= 0, "Index must be non-negative integer"
    assert os.path.splitext(args[0])[1] == os.path.splitext(args[2])[1], "Files must be the same type"
    with open(args[0], "r") as input_file:
        assert len(re.split(delimiter, input_file.next())) > int(args[1]), "Column does not exist in table"


# endregion


def like(*args):
    args = args[0]
    like_input_validation(args)
    input_file_path = args[0]
    column_index = int(args[1])
    regex = args[2]
    output_file_path = args[3]
    result_set = []  # Using list instead of set because set is not ordered
    pattern = re.compile(regex)
    with open(input_file_path, "r") as input_file:
        for line in input_file:
            value = re.split(delimiter, line)[column_index].rstrip()
            if pattern.match(value) and value not in result_set:
                result_set.append(line)

    with open(output_file_path, "w") as output_file:
        for line in result_set:
            output_file.write(str(line))


def like_input_validation(args):
    assert len(args) == 4, "Wrong number of arguments. This operation requires 4 arguments"
    assert os.path.isfile(args[0]), "Input file does not exist"
    assert isinstance(type(string_to_var(args[1])), int) and int(args[1]) >= 0, "Index must be non-negative integer"
    assert os.path.splitext(args[0])[1] == os.path.splitext(args[3])[1], "Files must be the same type"
    try:
        re.compile(args[2])
    except re.error:
        raise AssertionError("Invalid regular expression")
    with open(args[0], "r") as input_file:
        assert len(re.split(delimiter, input_file.next())) > int(args[1]), "Column does not exist in table"


def tables_structure_validation(file_1_path, file_2_path):
    with open(file_1_path, "r") as file_1:
        line_1 = file_1.next()
    with open(file_2_path, "r") as file_2:
        line_2 = file_2.next()
    split_1 = re.split(delimiter, line_1)
    split_2 = re.split(delimiter, line_2)
    assert len(split_1) == len(split_2), "Files don't have same number of columns"
    for i in range(len(split_1)):
        assert type(string_to_var(split_1[i])) == type(string_to_var(split_2[i])), "The tables' format does not match"


if __name__ == "__main__":
    try:
        functions_dict = \
            {
                "UNION": union,
                "SEPARATE": separate,
                "SEPERATE": separate,
                "DISTINCT": distinct,
                "LIKE": like
            }

        assert len(sys.argv) >= 2, "Missing operation. Available operations: {0}".format(
            ", ".join(functions_dict.keys()))

        action = sys.argv[1].upper()

        assert action in functions_dict, "Invalid operation {0}. Valid operations: {1}".format(action, ", ".join(
            functions_dict.keys()))

        functions_dict[action](sys.argv[2:])

    except Exception as ex:
        print "ERROR:", ex.message
