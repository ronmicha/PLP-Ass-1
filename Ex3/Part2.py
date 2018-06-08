import os
import sys

import pandas as pd
import numpy as np
from flask import Flask, request
from sklearn.model_selection import train_test_split

app = Flask(__name__)
MOVIE_ID_COL = 'movieId'
USER_ID_COL = 'userId'
RATING_COL = 'rating'
USER_CLUSTER_ID_COL = 'userClusterId'
MOVIE_CLUSTER_ID_COL = 'movieClusterId'


def get_average_rating(st, user_cluster_id, item_cluster_id):
    users_in_cluster = users_by_cluster[user_cluster_id]
    items_in_cluster = items_by_cluster[item_cluster_id]
    relevant_ratings_series = st.loc[st[MOVIE_ID_COL].isin(items_in_cluster) & st[USER_ID_COL].isin(users_in_cluster)][
        RATING_COL]
    if len(relevant_ratings_series) == 0:
        return AVG_SYSTEM_RATING
    return relevant_ratings_series.mean()


def get_B(st, u, v, k):
    calculate_users_and_items_by_cluster_id(k, u=u, v=v)
    b = np.empty((k, k))
    for user_cluster_id in range(k):
        for item_cluster_id in range(k):
            b[user_cluster_id, item_cluster_id] = get_average_rating(st, user_cluster_id, item_cluster_id)
    return b


def calculate_users_and_items_by_cluster_id(k, u, v):
    global users_by_cluster
    users_by_cluster = {user_cluster_id: list(np.where(u == user_cluster_id)[0]) for user_cluster_id in range(k)}
    global items_by_cluster
    items_by_cluster = {item_cluster_id: list(np.where(v == item_cluster_id)[0]) for item_cluster_id in range(k)}


def update_u(k, num_of_users, st, b):
    u = np.empty(num_of_users)
    for user_id in range(num_of_users):
        min_distance = sys.maxint
        min_cluster = 0
        for user_cluster_id in range(k):
            s = st[[st[USER_ID_COL] == user_id]].apply(
                lambda row: (row[RATING_COL] - b[user_cluster_id, row[MOVIE_CLUSTER_ID_COL]]) ** 2)
            if s.sum() < min_distance:
                min_distance = s.sum()
                min_cluster = user_cluster_id
        u[user_id - 1] = min_cluster


def build_b_file(k=10, t=10, epsilon=0.01, ratings_path="./ratings.csv", u_path="", v_path="", b_path=""):
    rating_df = pd.read_csv(ratings_path)
    v_arr = np.array(np.random.randint(0, k, rating_df[MOVIE_ID_COL].max()))
    u_arr = np.array(np.random.randint(0, k, len(rating_df[USER_ID_COL].unique())))
    st_df, sv_df = train_test_split(rating_df, test_size=0.2)
    global AVG_SYSTEM_RATING
    AVG_SYSTEM_RATING = st_df[RATING_COL].mean()

    st_df[MOVIE_CLUSTER_ID_COL] = st_df[MOVIE_ID_COL].apply(lambda x: v_arr[x - 1])
    b_arr = get_B(st=st_df, u=u_arr, v=v_arr, k=k)
    i = 0
    while i < t:  # and msre is improving
        u_arr = update_u(k=k, num_of_users=len(u_arr), st=st_df, b=b_arr)


@app.route('/', methods=['POST'])
def get_recommendation():
    assert 'n' in request.form, "Missing number of recommendations"
    assert 'userid' in request.form, "Missing user id"
    n = request.form['n']
    userid = request.form['userid']
    pass


if __name__ == '__main__':
    try:
        # assert len(sys.argv) == 9, "Wrong number of arguments. Please provide 9 arguments"
        # assert sys.argv[1] == 'ExtractCB', "Method must be ExtractCB"
        # assert os.path.basename(
        #     sys.argv[2]) == "ratings.csv", "Wrong input file provided. Input file must be named 'ratings.csv'"
        # assert os.path.isfile(sys.argv[2]), "Input file path is invalid or file doesn't exist"
        # assert isinstance(eval(sys.argv[3]), int), "K must be a number"
        # assert not eval(sys.argv[4]) or isinstance(eval(sys.argv[4]), int), "T must be a number or None"
        # assert not eval(sys.argv[5]) or isinstance(eval(sys.argv[5]), float), "epsilon must be a number or None"
        # assert os.path.isdir(sys.argv[6]), "U directory is invalid or doesn't exist"
        # assert os.path.isdir(sys.argv[7]), "V directory is invalid or doesn't exist"
        # assert os.path.isdir(sys.argv[8]), "B directory is invalid or doesn't exist"
        #
        # ratings_path = sys.argv[2]
        # k_size = int(sys.argv[3])
        # t_size = 10 if sys.argv[4] == 'null' else int(sys.argv[4])
        # epsilon = 0.01 if sys.argv[5] == 'null' else float(sys.argv[5])
        # u_path = sys.argv[6]
        # v_path = sys.argv[7]
        # b_path = sys.argv[8]

        build_b_file()

        app.run()
    except Exception as ex:
        print "Error!", ex.message
