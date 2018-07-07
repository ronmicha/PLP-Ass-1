import pandas as pd

users_df = None
transactions_df = None


# Original "users.json" had invalid structure, I modified it to be valid
def read_users_and_transactions_files(users_file_path, transactions_file_path):
    global users_df
    users_df = pd.read_json(users_file_path)
    global transactions_df
    transactions_df = pd.read_json(transactions_file_path)
    transactions_df = transactions_df.sort_values("date")


def part_a():
    transactions_df["weekday"] = pd.to_datetime(transactions_df["date"]).apply(lambda x: x.weekday())
    # income prediction features
    transactions_df["income"] = transactions_df["amount"] < 0
    transactions_df["total_incomes_last_week"] = ""
    transactions_df["total_incomes_last_month"] = ""
    transactions_df["num_of_incomes_last_week"] = ""
    transactions_df["num_of_incomes_last_month"] = ""
    # subscription prediction features
    transactions_df["same_name_last_week"] = ""
    transactions_df["same_name_last_month"] = ""
    transactions_df["same_categoryId_last_week"] = ""
    transactions_df["same_categoryId_last_month"] = ""
    transactions_df["same_amount_last_week"] = ""
    transactions_df["same_amount_last_month"] = ""
    print ""
    # subscription:
    # 1. same categoryId and name
    # 2. once every 7 days or 30 days
    # 3. deviation <= 20$ from average amount


if __name__ == '__main__':
    read_users_and_transactions_files("./users.json", "./transactions_clean.txt")
    part_a()
