import pandas as pd
import datetime as dt
from pandas.tseries.offsets import MonthEnd

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
    incomes_data = []
    for index, row in transactions_df.iterrows():
        last_week_incomes = get_last_n_days_incomes(row, 7)
        total_incomes_last_week = round(-last_week_incomes["amount"].sum(), 2) if not last_week_incomes.empty else None
        num_of_incomes_last_week = len(last_week_incomes.index)
        last_month_incomes = get_last_n_days_incomes(row, 30)
        total_incomes_last_month = round(-last_month_incomes["amount"].sum(), 2) if not last_month_incomes.empty else None
        num_of_incomes_last_month = len(last_month_incomes.index)
        incomes_data.append([total_incomes_last_week, num_of_incomes_last_week, total_incomes_last_month, num_of_incomes_last_month])
    incomes_df = pd.DataFrame(incomes_data, columns=["total_incomes_last_week",
                                                     "num_of_incomes_last_week",
                                                     "total_incomes_last_month",
                                                     "num_of_incomes_last_month"])

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


def get_last_n_days_incomes(row, n):
    if n == 7:
        start_date = row["date"] - pd.DateOffset(days=7 + int(row["weekday"]))
        end_date = start_date + pd.DateOffset(days=6)
    else:  # n == 30
        start_date = row["date"] - pd.DateOffset(months=1, days=int(row["weekday"]))
        end_date = start_date + MonthEnd()
    last_n_days_incomes = transactions_df[(transactions_df["userId"] == row["userId"]) &
                                          (transactions_df["income"]) &
                                          (transactions_df["date"] >= start_date) &
                                          (transactions_df["date"] <= end_date)]
    return last_n_days_incomes


if __name__ == '__main__':
    read_users_and_transactions_files("./users.json", "./transactions_clean.txt")
    part_a()
