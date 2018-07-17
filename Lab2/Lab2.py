# *********** Use Python 2 ***********
import json
import pickle
import numpy as np
import pandas as pd
from difflib import SequenceMatcher
from sklearn.svm import SVC, SVR
from sklearn.naive_bayes import GaussianNB
from pandas.tseries.offsets import MonthBegin
from sklearn.linear_model import SGDClassifier, SGDRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.base import clone
from sklearn.metrics import precision_score
from flask import Flask, request, jsonify

flask_app = Flask(__name__)

# region Column Names Enum
# Given Features:
CATEGORY = "category"
USER_ID = "userId"
WEEKDAY = "weekday"
WORK_WEEK = "work_week"
MONTH = "month"
DATE = "date"
DAY = "day"
INCOME = "income"
AMOUNT = "amount"
NAME = "name"
CATEGORY_ID = "categoryId"
# Income Prediction Features:
TOTAL_INCOMES_LAST_WEEK = "total_incomes_last_week"
NUM_OF_INCOMES_LAST_WEEK = "num_of_incomes_last_week"
TOTAL_INCOMES_LAST_MONTH = "total_incomes_last_month"
NUM_OF_INCOMES_LAST_MONTH = "num_of_incomes_last_month"
MEAN_INCOME_LAST_WEEK = "mean_income_last_week"
MEAN_INCOME_LAST_MONTH = "mean_income_last_month"
# Subscription Prediction Features:
LAST_WEEK_CHARGE_SAME_PRICE = "last_week_charge_same_price"
LAST_MONTH_CHARGE_SAME_PRICE = "last_month_charge_same_price"
LAST_WEEK_CHARGE_SAME_CATEGORY = "last_week_charge_same_category"
LAST_MONTH_CHARGE_SAME_CATEGORY = "last_month_charge_same_category"
LAST_WEEK_SAME_NAME = "last_week_same_name "
LAST_MONTH_SAME_NAME = "last_month_same_name"
# Target Features:
SUBSCRIPTION = "subscription"
WEEKLY_INCOME = "weekly_income"
MONTHLY_INCOME = "monthly_income"
# Subscription Target Value Calculation Features - not to be used in prediction model!:
SAME_NAME_LAST_WEEK = "same_name_last_week"
SAME_NAME_LAST_MONTH = "same_name_last_month"
SAME_CATEGORY_ID_LAST_WEEK = "same_categoryId_last_week"
SAME_CATEGORY_ID_LAST_MONTH = "same_categoryId_last_month"
SAME_AMOUNT_LAST_WEEK = "same_amount_last_week"
SAME_AMOUNT_LAST_MONTH = "same_amount_last_month"
# endregion

# region Globals
users_df = None
transactions_df = None
models = None
all_categories = [u'Bicycles', u'Shops', u'Food and Drink', u'Restaurants', u'Car Service', u'Ride Share', u'Travel',
                  u'Airlines and Aviation Services', u'Coffee Shop', u'Gyms and Fitness Centers', u'Recreation', u'Deposit', u'Transfer',
                  u'Credit Card', u'Payment', u'Credit', u'Discount Stores', u'Service', u'Telecommunication Services', u'Music, Video and DVD',
                  u'Financial', u'Computers and Electronics', u'Video Games', u'Warehouses and Wholesale Stores', u'Debit', u'Digital Purchase',
                  u'Supermarkets and Groceries', u'Cable', u'Gas Stations', u'Department Stores', u'Bank Fees', u'Overdraft', u'Interest',
                  u'Interest Charged', u'Wire Transfer', 'subscription_cat', u'Personal Care', u'ATM', u'Withdrawal', u'Pharmacies']
weekly_income_prediction_features = [WORK_WEEK, AMOUNT, INCOME] + [TOTAL_INCOMES_LAST_MONTH, NUM_OF_INCOMES_LAST_MONTH,
                                                                   MEAN_INCOME_LAST_WEEK] + all_categories
monthly_income_prediction_features = [DAY, AMOUNT, INCOME] + [TOTAL_INCOMES_LAST_WEEK, NUM_OF_INCOMES_LAST_WEEK,
                                                              MEAN_INCOME_LAST_MONTH] + all_categories
subscription_prediction_features = all_categories + \
                                   [LAST_MONTH_CHARGE_SAME_CATEGORY, LAST_MONTH_CHARGE_SAME_PRICE, LAST_MONTH_SAME_NAME] + \
                                   [LAST_WEEK_CHARGE_SAME_CATEGORY, LAST_WEEK_CHARGE_SAME_PRICE, LAST_WEEK_SAME_NAME]


# endregion

# Original "users.json" had invalid structure, I modified it to be valid
def read_users_and_transactions_files(users_file_path, transactions_file_path):
    global users_df
    global transactions_df

    users_df = pd.read_json(users_file_path)
    transactions_df = pd.read_json(transactions_file_path)
    transactions_df = transactions_df.sort_values(DATE)


# region Part A
def part_a(data_df, fill_target_values=False):
    data_df[DATE] = pd.to_datetime(data_df[DATE])
    data_df[WEEKDAY] = pd.to_datetime(data_df[DATE]).apply(lambda x: x.weekday())
    data_df[WORK_WEEK] = pd.to_datetime(data_df[DATE]).apply(lambda x: x.isocalendar()[1])
    data_df[MONTH] = pd.to_datetime(data_df[DATE]).apply(lambda x: x.month)
    data_df[DAY] = pd.to_datetime(data_df[DATE]).apply(lambda x: x.day)
    # categories_df = data_df[CATEGORY].apply(
    #     lambda x: pd.Series({k if k.lower() != 'subscription' else 'subscription_cat': 1 for v, k in enumerate(x)})).fillna(0)
    # data_df = pd.concat([data_df, categories_df], axis=1)
    data_df[INCOME] = data_df[AMOUNT] < 0
    additional_features_data = []
    features_for_subscription_label = []

    for index, row in data_df.iterrows():
        # Discrediting Categories:
        categories_data = [1 if category in row[CATEGORY] else 0 for category in all_categories]
        last_week_charges = get_from_start_of_week_or_month(row, 7, incomes=False)
        last_month_charges = get_from_start_of_week_or_month(row, 30, incomes=False)
        # Subscription features:
        last_week_charge_same_price_df = last_week_charges[abs(last_week_charges[AMOUNT] - row[AMOUNT]) < 20]
        last_month_charge_same_price_df = last_month_charges[abs(last_month_charges[AMOUNT] - row[AMOUNT]) < 20]
        last_week_charge_same_category_df = last_week_charges[CATEGORY].apply(lambda x: x == row[CATEGORY])
        last_month_charge_same_category_df = last_month_charges[CATEGORY].apply(lambda x: x == row[CATEGORY])
        last_week_same_name_df = last_week_charges[NAME].apply(lambda x: SequenceMatcher(None, x, row[NAME]).ratio() >= 0.7)
        last_month_same_name_df = last_month_charges[NAME].apply(lambda x: SequenceMatcher(None, x, row[NAME]).ratio() >= 0.7)
        last_week_charge_same_price = not last_week_charge_same_price_df.empty
        last_month_charge_same_price = not last_month_charge_same_price_df.empty
        last_week_charge_same_category = not last_week_charge_same_category_df.empty
        last_month_charge_same_category = not last_month_charge_same_category_df.empty
        last_week_same_name = not last_week_same_name_df.empty
        last_month_same_name = not last_month_same_name_df.empty
        # ToDo delete this?
        # last_week_charge_same_price_avg_amount = last_week_charge_same_price_df[AMOUNT].mean() if last_week_charge_same_price else 0
        # last_month_charge_same_price_avg_amount = last_month_charge_same_price_df[AMOUNT].mean() if last_month_charge_same_price else 0
        # # last_week_charge_same_category_avg_amount = last_week_charge_same_category_df[AMOUNT].mean()
        # # last_month_charge_same_category_avg_amount = last_month_charge_same_category_df[AMOUNT].mean()
        # # last_week_same_name_avg_amount = last_week_same_name_df[AMOUNT].mean()
        # # last_month_same_name_avg_amount = last_month_same_name_df[AMOUNT].mean()
        # Income features:
        last_week_incomes = get_from_start_of_week_or_month(row, 7)
        last_month_incomes = get_from_start_of_week_or_month(row, 30)
        total_incomes_last_week = round(-last_week_incomes[AMOUNT].sum(), 2) if not last_week_incomes.empty else 0
        total_incomes_last_month = round(-last_month_incomes[AMOUNT].sum(), 2) if not last_month_incomes.empty else 0
        num_of_incomes_last_week = len(last_week_incomes.index)
        num_of_incomes_last_month = len(last_month_incomes.index)
        mean_income_last_week = -last_week_incomes[AMOUNT].mean() if not last_week_incomes.empty else 0
        mean_income_last_month = -last_month_incomes[AMOUNT].mean() if not last_month_incomes.empty else 0
        # This data will be used in the model:
        additional_features_data.append([  # Income:
                                            total_incomes_last_week,
                                            total_incomes_last_month,
                                            num_of_incomes_last_week,
                                            num_of_incomes_last_month,
                                            mean_income_last_week,
                                            mean_income_last_month,
                                            # Subscription:
                                            last_week_charge_same_price,
                                            last_week_charge_same_category,
                                            last_month_charge_same_price,
                                            last_month_charge_same_category,
                                            last_week_same_name,
                                            last_month_same_name] + categories_data)
        # Subscription features - won't be used to predict:
        if fill_target_values:
            same_amount_last_week = same_attr_n_days_ago(row, AMOUNT, 7, lambda a, b: abs(a - b) <= 20)
            same_amount_last_month = same_attr_n_days_ago(row, AMOUNT, 30, lambda a, b: abs(a - b) <= 20)
            same_categoryid_last_week = same_attr_n_days_ago(row, CATEGORY_ID, 7, lambda a, b: a == b)
            same_categoryid_last_month = same_attr_n_days_ago(row, CATEGORY_ID, 30, lambda a, b: a == b)
            # This data won't be used in the model, only to label the Subscription column:
            features_for_subscription_label.append([same_amount_last_week,
                                                    same_amount_last_month,
                                                    same_categoryid_last_week,
                                                    same_categoryid_last_month])

    additional_features_df = pd.DataFrame(additional_features_data, columns=[  # Income:
                                                                                TOTAL_INCOMES_LAST_WEEK,
                                                                                TOTAL_INCOMES_LAST_MONTH,
                                                                                NUM_OF_INCOMES_LAST_WEEK,
                                                                                NUM_OF_INCOMES_LAST_MONTH,
                                                                                MEAN_INCOME_LAST_WEEK,
                                                                                MEAN_INCOME_LAST_MONTH,
                                                                                # Subscription:
                                                                                LAST_WEEK_CHARGE_SAME_PRICE,
                                                                                LAST_WEEK_CHARGE_SAME_CATEGORY,
                                                                                LAST_MONTH_CHARGE_SAME_PRICE,
                                                                                LAST_MONTH_CHARGE_SAME_CATEGORY,
                                                                                LAST_WEEK_SAME_NAME,
                                                                                LAST_MONTH_SAME_NAME] + all_categories)
    all_data_df = pd.concat([data_df, additional_features_df], axis=1)

    if fill_target_values:
        # Calculate Subscription target values:
        features_for_subscription_label_df = pd.DataFrame(features_for_subscription_label, columns=[SAME_AMOUNT_LAST_WEEK,
                                                                                                    SAME_AMOUNT_LAST_MONTH,
                                                                                                    SAME_CATEGORY_ID_LAST_WEEK,
                                                                                                    SAME_CATEGORY_ID_LAST_MONTH])
        all_data_df[SUBSCRIPTION] = \
            (features_for_subscription_label_df[SAME_AMOUNT_LAST_WEEK] & features_for_subscription_label_df[SAME_CATEGORY_ID_LAST_WEEK]) | \
            (features_for_subscription_label_df[SAME_AMOUNT_LAST_MONTH] & features_for_subscription_label_df[SAME_CATEGORY_ID_LAST_MONTH])
        # Calculate Income target values:
        user_weekly_income = all_data_df[all_data_df[INCOME]][[USER_ID, WORK_WEEK, AMOUNT]].groupby(by=[USER_ID, WORK_WEEK], as_index=False).sum()
        user_weekly_income.rename(columns={AMOUNT: WEEKLY_INCOME}, inplace=True)
        user_weekly_income[WEEKLY_INCOME] = -user_weekly_income[WEEKLY_INCOME]
        user_monthly_income = all_data_df[all_data_df[INCOME]][[USER_ID, MONTH, AMOUNT]].groupby(by=[USER_ID, MONTH], as_index=False).sum()
        user_monthly_income.rename(columns={AMOUNT: MONTHLY_INCOME}, inplace=True)
        user_monthly_income[MONTHLY_INCOME] = -user_monthly_income[MONTHLY_INCOME]
        all_data_df = all_data_df.merge(user_weekly_income, on=[USER_ID, WORK_WEEK])
        all_data_df = all_data_df.merge(user_monthly_income, on=[USER_ID, MONTH])

    return all_data_df


def get_from_start_of_week_or_month(row, n, incomes=True):
    if n == 7:
        if row[WEEKDAY] != 0:
            start_date = row[DATE] - pd.DateOffset(days=int(row[WEEKDAY]))
            end_date = row[DATE] - pd.DateOffset(days=1)
        else:  # Look at previous week
            start_date = row[DATE] - pd.DateOffset(days=7)
            end_date = row[DATE] - pd.DateOffset(days=1)
    else:  # n == 30
        if row[DAY] != 1:
            start_date = row[DATE] - MonthBegin()
            end_date = row[DATE] - pd.DateOffset(days=1)
        else:  # Look at previous month
            start_date = row[DATE] - pd.DateOffset(months=1)
            end_date = row[DATE] - pd.DateOffset(days=1)
    last_n_days = transactions_df[(transactions_df[USER_ID] == row[USER_ID]) &
                                  (transactions_df[INCOME] == incomes) &
                                  (transactions_df[DATE] >= start_date) &
                                  (transactions_df[DATE] <= end_date)]
    return last_n_days


def same_attr_n_days_ago(row, attr, n, compare_func):
    last_n_days_transaction = transactions_df[(transactions_df[USER_ID] == row[USER_ID]) &
                                              (transactions_df[INCOME] == False) &
                                              (transactions_df[DATE] == row[DATE] - pd.DateOffset(days=n))]
    return last_n_days_transaction[attr].apply(lambda x: compare_func(x, row[attr])).any()


# endregion

# region Part B


def part_b(data_df):
    subscription_model = build_subscription_model(data_df)
    users_income_models = build_income_models(data_df)
    models_dict = {"subscription": subscription_model, "incomes": users_income_models}
    pickle.dump(models_dict, open('models', 'wb'))


def build_subscription_model(data_df):
    X = data_df[subscription_prediction_features]
    Y = data_df[SUBSCRIPTION]
    x_train, x_test = np.split(X, [int(0.8 * len(X.index))])
    y_train, y_test = np.split(Y, [int(0.8 * len(Y.index))])

    classification_models = {
        # "SVC": SVC(),
        # "SGD": SGDClassifier(),
        # "Naive Bayes": GaussianNB(),
        "MLP": MLPClassifier()
        # "Decision Tree": DecisionTreeClassifier()
    }

    # Todo choose a specific model and use it
    for name, model in classification_models.items():
        model.fit(x_train, y_train)
        print "Precision for subscription using", name, precision_score(y_test, model.predict(x_test))
        return model


def build_income_models(data_df):
    regression_models = {"SVR": SVR(),
                         "SGD": SGDRegressor(),
                         "MLP": MLPRegressor(),
                         "Decision Tree": DecisionTreeRegressor(),
                         "Random Forest": RandomForestRegressor(),
                         "Gradient Boost": GradientBoostingRegressor()}
    user_models = {}
    # ToDo choose a specific model and use it
    for name, model in regression_models.items():
        average_month_mse = 0
        average_week_mse = 0
        for user_id in data_df[USER_ID].unique():
            user_models[user_id] = {}
            user_df = data_df[(data_df[USER_ID] == user_id) & (data_df[INCOME])]
            # Sort from beginning to end of month/week
            X_month = user_df[monthly_income_prediction_features]
            X_week = user_df[weekly_income_prediction_features]
            Y_month = user_df[MONTHLY_INCOME]
            Y_week = user_df[WEEKLY_INCOME]
            x_train_month, x_test_month = np.split(X_month, [int(0.8 * len(X_month.index))])
            x_train_week, x_test_week = np.split(X_week, [int(0.8 * len(X_week.index))])
            y_month_train, y_month_test = np.split(Y_month, [int(0.8 * len(Y_month.index))])
            y_week_train, y_week_test = np.split(Y_week, [int(0.8 * len(Y_week.index))])

            # Month
            month_model = clone(model)
            month_model.fit(x_train_month, y_month_train)
            average_month_mse += mean_squared_error(y_month_test, month_model.predict(x_test_month)) ** 0.5
            print "User ID:", user_id, "monthly using", name, "Mean Error:", mean_squared_error(y_month_test,
                                                                                                month_model.predict(x_test_month)) ** 0.5
            user_models[user_id]['monthly'] = month_model
            # Week
            week_model = clone(model)
            week_model.fit(x_train_week, y_week_train)
            average_week_mse += mean_squared_error(y_week_test, week_model.predict(x_test_week)) ** 0.5
            print "User ID:", user_id, "weekly using", name, "Mean Error:", mean_squared_error(y_week_test, week_model.predict(x_test_week)) ** 0.5
            user_models[user_id]['weekly'] = week_model
        # print "Monthly avg MSE using", name, ":", average_month_mse / len(data_df[USER_ID].unique())
        # print "Weekly avg MSE using", name, ":", average_week_mse / len(data_df[USER_ID].unique())
    return user_models


# endregion

# region Part C
def part_c():
    flask_app.run()


@flask_app.before_first_request
def load_files():
    global models, transactions_df
    transactions_df = pd.read_csv('data.csv')
    transactions_df[DATE] = pd.to_datetime(transactions_df[DATE])
    # Use only train data, as Moshe requested
    transactions_df = np.split(transactions_df.sort_values(DATE), [int(0.8 * len(transactions_df.index))])[0]
    models = pickle.load(open('models', 'rb'))


@flask_app.route('/', methods=['POST'])
def get_predictions():
    try:
        data = json.loads(request.data)
        assert 'trans' in data, "Missing transaction"
        return jsonify(predict(data))
    except Exception as e:
        return repr(e), 500


def predict(data):
    transaction = ready_transaction_to_model(data)
    if transaction[USER_ID][0] not in models['incomes']:
        transaction = transactions_df.sample(n=1)
    return {
        "subscription": False if transaction[INCOME].iloc[0] else bool(
            models['subscription'].predict(transaction[subscription_prediction_features])[0]),
        "weeklyIncome": float(models['incomes'][transaction[USER_ID].iloc[0]]['weekly'].predict(transaction[weekly_income_prediction_features])[0]),
        "monthlyIncome": float(models['incomes'][transaction[USER_ID].iloc[0]]['monthly'].predict(transaction[monthly_income_prediction_features])[0])
    }


def ready_transaction_to_model(data):
    trans_df = pd.DataFrame.from_dict(data).transpose().reset_index().drop('index', axis=1)
    return part_a(trans_df, fill_target_values=False)


# endregion

if __name__ == '__main__':
    #     read_users_and_transactions_files("./users.json", "./transactions_clean.json")
    #     all_data = part_a(transactions_df, fill_target_values=True)
    #     all_data.to_csv('data.csv', index=False)

    # debug
    # all_data = pd.read_csv('data.csv')
    # end debug

    # part_b(all_data)
    part_c()
