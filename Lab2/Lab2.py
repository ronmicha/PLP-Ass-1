import pandas as pd
import datetime as dt
from difflib import SequenceMatcher
from pandas.tseries.offsets import MonthEnd

# region Column Names Enum
USERID = "userId"
WEEKDAY = "weekday"
DATE = "date"
INCOME = "income"
AMOUNT = "amount"
NAME = "name"
TOTAL_INCOMES_LAST_WEEK = "total_incomes_last_week"
NUM_OF_INCOMES_LAST_WEEK = "num_of_incomes_last_week"
TOTAL_INCOMES_LAST_MONTH = "total_incomes_last_month"
NUM_OF_INCOMES_LAST_MONTH = "num_of_incomes_last_month"
SAME_NAME_LAST_WEEK = "same_name_last_week"
SAME_NAME_LAST_MONTH = "same_name_last_month"
SAME_CATEGORYID_LAST_WEEK = "same_categoryId_last_week"
SAME_CATEGORYID_LAST_MONTH = "same_categoryId_last_month"
SAME_AMOUNT_LAST_WEEK = "same_amount_last_week"
SAME_AMOUNT_LAST_MONTH = "same_amount_last_month"
# endregion

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
    transactions_df[WEEKDAY] = pd.to_datetime(transactions_df[DATE]).apply(lambda x: x.weekday())

    # income prediction features
    transactions_df[INCOME] = transactions_df[AMOUNT] < 0
    incomes_data = []
    for index, row in transactions_df.iterrows():
        last_week_incomes = get_last_n_days_incomes(row, 7)
        total_incomes_last_week = round(-last_week_incomes[AMOUNT].sum(), 2) if not last_week_incomes.empty else None
        num_of_incomes_last_week = len(last_week_incomes.index)
        last_month_incomes = get_last_n_days_incomes(row, 30)
        total_incomes_last_month = round(-last_month_incomes[AMOUNT].sum(),
                                         2) if not last_month_incomes.empty else None
        num_of_incomes_last_month = len(last_month_incomes.index)
        same_name_last_week = same_attr_past_n_days(row, NAME, 7, 0.7)
        incomes_data.append(
            [total_incomes_last_week, num_of_incomes_last_week, total_incomes_last_month, num_of_incomes_last_month])
    incomes_df = pd.DataFrame(incomes_data, columns=[TOTAL_INCOMES_LAST_WEEK,
                                                     NUM_OF_INCOMES_LAST_WEEK,
                                                     TOTAL_INCOMES_LAST_MONTH,
                                                     NUM_OF_INCOMES_LAST_MONTH])

    # subscription prediction features
    transactions_df[SAME_NAME_LAST_MONTH] = ""
    transactions_df[SAME_CATEGORYID_LAST_WEEK] = ""
    transactions_df[SAME_CATEGORYID_LAST_MONTH] = ""
    transactions_df[SAME_AMOUNT_LAST_WEEK] = ""
    transactions_df[SAME_AMOUNT_LAST_MONTH] = ""
    print ""
    # subscription:
    # 1. same categoryId and name
    # 2. once every 7 days or 30 days
    # 3. deviation <= 20$ from average amount


def get_last_n_days_incomes(row, n):
    if n == 7:
        start_date = row[DATE] - pd.DateOffset(days=7 + int(row[WEEKDAY]))
        end_date = start_date + pd.DateOffset(days=6)
    else:  # n == 30
        start_date = row[DATE] - pd.DateOffset(months=1, days=int(row[WEEKDAY]))
        end_date = start_date + MonthEnd()
    last_n_days_incomes = transactions_df[(transactions_df[USERID] == row[USERID]) &
                                          (transactions_df[INCOME]) &
                                          (transactions_df[DATE] >= start_date) &
                                          (transactions_df[DATE] <= end_date)]
    return last_n_days_incomes


def same_attr_past_n_days(row, attr, n, similarity=1.0):
    last_n_days_transaction = transactions_df[(transactions_df[USERID] == row[USERID]) &
                                              (transactions_df[INCOME] == False) &
                                              (transactions_df[DATE] == row[DATE] - pd.DateOffset(days=n))]
    return last_n_days_transaction[attr].apply(
        lambda x: SequenceMatcher(None, x, row[attr]).ratio() >= similarity).any()


if __name__ == '__main__':
    read_users_and_transactions_files("./users.json", "./transactions_clean.json")
    part_a()
