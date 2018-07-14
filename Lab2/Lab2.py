from difflib import SequenceMatcher
import numpy as np
import pandas as pd
from pandas.tseries.offsets import MonthEnd, MonthBegin
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier

# region Column Names Enum
CATEGORY = "category"
USERID = "userId"
WEEKDAY = "weekday"
WORK_WEEK = "work_week"
MONTH = "month"
DATE = "date"
INCOME = "income"
AMOUNT = "amount"
NAME = "name"
CATEGORYID = "categoryId"
SUBSCRIPTION = "subscription"
WEEKLY_INCOME = "weekly_income"
MONTHLY_INCOME = "monthly_income"
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
all_categories = None


# Original "users.json" had invalid structure, I modified it to be valid
def read_users_and_transactions_files(users_file_path, transactions_file_path):
    global users_df
    global transactions_df

    users_df = pd.read_json(users_file_path)
    transactions_df = pd.read_json(transactions_file_path)
    transactions_df = transactions_df.sort_values(DATE)


# region Part A
def part_a():
    global all_categories
    global transactions_df

    transactions_df[WEEKDAY] = pd.to_datetime(transactions_df[DATE]).apply(lambda x: x.weekday())
    transactions_df[WORK_WEEK] = pd.to_datetime(transactions_df[DATE]).apply(lambda x: x.isocalendar()[1])
    transactions_df[MONTH] = pd.to_datetime(transactions_df[DATE]).apply(lambda x: x.month)
    categories_df = transactions_df[CATEGORY].apply(
        lambda x: pd.Series({k if k.lower() != 'subscription' else 'subscription_cat': 1 for v, k in enumerate(x)})).fillna(0)
    all_categories = list(categories_df.columns)
    transactions_df = pd.concat([transactions_df, categories_df], axis=1)
    transactions_df[INCOME] = transactions_df[AMOUNT] < 0
    additional_features_data = []

    for index, row in transactions_df.iterrows():
        # Income features:
        last_week_incomes = get_last_n_days_incomes(row, 7)
        last_month_incomes = get_last_n_days_incomes(row, 30)
        total_incomes_last_week = round(-last_week_incomes[AMOUNT].sum(), 2) if not last_week_incomes.empty else None
        num_of_incomes_last_week = len(last_week_incomes.index)
        total_incomes_last_month = round(-last_month_incomes[AMOUNT].sum(), 2) if not last_month_incomes.empty else None
        num_of_incomes_last_month = len(last_month_incomes.index)
        # Subscription features:
        same_name_last_week = same_attr_past_n_days(row, NAME, 7, lambda a, b: SequenceMatcher(None, a, b).ratio() >= 0.7)
        same_name_last_month = same_attr_past_n_days(row, NAME, 30, lambda a, b: SequenceMatcher(None, a, b).ratio() >= 0.7)
        same_amount_last_week = same_attr_past_n_days(row, AMOUNT, 7, lambda a, b: abs(a - b) <= 20)
        same_amount_last_month = same_attr_past_n_days(row, AMOUNT, 30, lambda a, b: abs(a - b) <= 20)
        same_categoryid_last_week = same_attr_past_n_days(row, CATEGORYID, 7, lambda a, b: a == b)
        same_categoryid_last_month = same_attr_past_n_days(row, CATEGORYID, 30, lambda a, b: a == b)
        additional_features_data.append([total_incomes_last_week,
                                         num_of_incomes_last_week,
                                         total_incomes_last_month,
                                         num_of_incomes_last_month,
                                         same_name_last_week,
                                         same_name_last_month,
                                         same_amount_last_week,
                                         same_amount_last_month,
                                         same_categoryid_last_week,
                                         same_categoryid_last_month])

    additional_features_df = pd.DataFrame(additional_features_data, columns=[TOTAL_INCOMES_LAST_WEEK,
                                                                             NUM_OF_INCOMES_LAST_WEEK,
                                                                             TOTAL_INCOMES_LAST_MONTH,
                                                                             NUM_OF_INCOMES_LAST_MONTH,
                                                                             SAME_NAME_LAST_WEEK,
                                                                             SAME_NAME_LAST_MONTH,
                                                                             SAME_AMOUNT_LAST_WEEK,
                                                                             SAME_AMOUNT_LAST_MONTH,
                                                                             SAME_CATEGORYID_LAST_WEEK,
                                                                             SAME_CATEGORYID_LAST_MONTH])
    # Calculate Subscription target values:
    all_data_df = pd.concat([transactions_df, additional_features_df], axis=1)
    all_data_df[SUBSCRIPTION] = \
        (all_data_df[SAME_NAME_LAST_WEEK] & all_data_df[SAME_AMOUNT_LAST_WEEK] & all_data_df[SAME_CATEGORYID_LAST_WEEK]) | \
        (all_data_df[SAME_NAME_LAST_MONTH] & all_data_df[SAME_AMOUNT_LAST_MONTH] & all_data_df[SAME_CATEGORYID_LAST_MONTH])
    # Calculate Income target values:
    user_weekly_income = all_data_df[all_data_df[INCOME]][[USERID, WORK_WEEK, AMOUNT]].groupby(by=[USERID, WORK_WEEK], as_index=False).sum()
    user_weekly_income.rename(columns={AMOUNT: WEEKLY_INCOME}, inplace=True)
    user_weekly_income[WEEKLY_INCOME] = -user_weekly_income[WEEKLY_INCOME]
    user_monthly_income = all_data_df[all_data_df[INCOME]][[USERID, MONTH, AMOUNT]].groupby(by=[USERID, MONTH], as_index=False).sum()
    user_monthly_income.rename(columns={AMOUNT: MONTHLY_INCOME}, inplace=True)
    user_monthly_income[MONTHLY_INCOME] = -user_monthly_income[MONTHLY_INCOME]
    all_data_df = all_data_df.merge(user_weekly_income, on=[USERID, WORK_WEEK])
    all_data_df = all_data_df.merge(user_monthly_income, on=[USERID, MONTH])

    return all_data_df


def get_last_n_days_incomes(row, n):
    if n == 7:
        start_date = row[DATE] - pd.DateOffset(days=int(row[WEEKDAY]))
        end_date = row[DATE]
    else:  # n == 30
        start_date = row[DATE] - MonthBegin()  # pd.DateOffset(months=1, days=int(row[WEEKDAY]))
        end_date = row[DATE]
    last_n_days_incomes = transactions_df[(transactions_df[USERID] == row[USERID]) &
                                          (transactions_df[INCOME]) &
                                          (transactions_df[DATE] >= start_date) &
                                          (transactions_df[DATE] <= end_date)]
    return last_n_days_incomes


def same_attr_past_n_days(row, attr, n, compare_func):
    last_n_days_transaction = transactions_df[(transactions_df[USERID] == row[USERID]) &
                                              (transactions_df[INCOME] == False) &
                                              (transactions_df[DATE] == row[DATE] - pd.DateOffset(days=n))]
    return last_n_days_transaction[attr].apply(lambda x: compare_func(x, row[attr])).any()


# endregion

# region Part B


def part_b(data_df):
    build_subscription_model(data_df)
    build_income_models(data_df)


def build_subscription_model(data_df):
    features_cols = all_categories + [SAME_CATEGORYID_LAST_MONTH, SAME_CATEGORYID_LAST_WEEK,
                                      SAME_AMOUNT_LAST_MONTH, SAME_AMOUNT_LAST_WEEK,
                                      SAME_NAME_LAST_MONTH, SAME_NAME_LAST_WEEK]
    X = data_df[features_cols]
    Y = data_df[SUBSCRIPTION]
    x_train, x_test = np.split(X, [int(0.8 * len(X.index))])
    y_train, y_test = np.split(Y, [int(0.8 * len(Y.index))])

    models = {"SVC": SVC(),
              "SGD": SGDClassifier(),
              "Naive Bayes": GaussianNB(),
              "MLP": MLPClassifier(),
              "Decision Tree": DecisionTreeClassifier()}

    for name, model in models.items():
        model.fit(x_train, y_train)
        print name, ":", model.score(x_test, y_test)


def build_income_models(data_df):
    pass


# endregion


if __name__ == '__main__':
    read_users_and_transactions_files("./users.json", "./transactions_clean.json")
    # all_data = part_a()
    # all_data.to_csv('data.csv', index=False)

    # debug
    all_data = pd.read_csv('data.csv')

    global all_categories
    all_categories = [u'Bicycles', u'Shops', u'Food and Drink', u'Restaurants', u'Car Service', u'Ride Share', u'Travel',
                      u'Airlines and Aviation Services', u'Coffee Shop', u'Gyms and Fitness Centers', u'Recreation', u'Deposit', u'Transfer',
                      u'Credit Card', u'Payment', u'Credit', u'Discount Stores', u'Service', u'Telecommunication Services', u'Music, Video and DVD',
                      u'Financial', u'Computers and Electronics', u'Video Games', u'Warehouses and Wholesale Stores', u'Debit', u'Digital Purchase',
                      u'Supermarkets and Groceries', u'Cable', u'Gas Stations', u'Department Stores', u'Bank Fees', u'Overdraft', u'Interest',
                      u'Interest Charged', u'Wire Transfer', 'subscription_cat', u'Personal Care', u'ATM', u'Withdrawal', u'Pharmacies']
    part_b(all_data)
