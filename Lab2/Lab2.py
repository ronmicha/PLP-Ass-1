import json


def part_a(transactions_file_path):
    with open(transactions_file_path) as json_file:
        transactions = json.load(json_file)
    for transaction in transactions:
        print transaction


if __name__ == '__main__':
    part_a("./transactions_clean.txt")
