import os
import json
import sys
import traceback
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from sklearn.model_selection import train_test_split

app = Flask(__name__)
MOVIE_ID_COL = 'movieId'
USER_ID_COL = 'userId'
RATING_COL = 'rating'
USER_CLUSTER_ID_COL = 'userClusterId'
MOVIE_CLUSTER_ID_COL = 'movieClusterId'

u_path = "u.csv"
v_path = "v.csv"
b_path = "b.csv"


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
    for user_id in range(1, num_of_users + 1):
        min_error = sys.maxint
        min_cluster = 0
        user_ratings = st[st[USER_ID_COL] == user_id]
        for user_cluster_id in range(k):
            error_series = (user_ratings[RATING_COL].values - b[
                user_cluster_id, user_ratings[MOVIE_CLUSTER_ID_COL].values]) ** 2
            if len(error_series) == 0:
                break
            error = error_series.sum()
            if error < min_error:
                min_error = error
                min_cluster = user_cluster_id
        u[user_id - 1] = min_cluster
    return u.astype('int32')


def update_v(k, num_of_movies, st, b):
    v = np.empty(num_of_movies)
    for movie_id in st[MOVIE_ID_COL].unique():
        min_error = sys.maxint
        min_cluster = 0
        movie_ratings = st[st[MOVIE_ID_COL] == movie_id]
        for movie_cluster_id in range(k):
            errors_series = (movie_ratings[RATING_COL].values - b[
                movie_ratings[USER_CLUSTER_ID_COL].values, movie_cluster_id]) ** 2
            if len(errors_series) == 0:
                break
            error = errors_series.sum()
            if error < min_error:
                min_error = error
                min_cluster = movie_cluster_id
        v[movie_id - 1] = min_cluster
    return v.astype('int32')


def get_rmse(sv, b, u, v):
    # mse = sv.apply(lambda row: (row[RATING_COL] - b[u[int(row[USER_ID_COL])], v[int(row[MOVIE_ID_COL])]]) ** 2,
    #                axis=1).mean()
    mse = ((sv[RATING_COL].values - b[u[sv[USER_ID_COL].values], v[sv[MOVIE_ID_COL].values]]) ** 2).mean()
    return mse ** 0.5


def build_b_file(k=20, t=10, epsilon=0.01, ratings_path="./ratings.csv"):
    rating_df = pd.read_csv(ratings_path)
    rating_df.sort_values(by='timestamp', inplace=True)
    v_arr = np.array(np.random.randint(0, k, rating_df[MOVIE_ID_COL].max() + 1))
    u_arr = np.array(np.random.randint(0, k, len(rating_df[USER_ID_COL].unique())))
    st_df, sv_df = train_test_split(rating_df, test_size=0.2, shuffle=False)
    global AVG_SYSTEM_RATING
    AVG_SYSTEM_RATING = st_df[RATING_COL].mean()

    st_df[MOVIE_CLUSTER_ID_COL] = v_arr[st_df[MOVIE_ID_COL].values - 1]
    st_df[USER_CLUSTER_ID_COL] = u_arr[st_df[USER_ID_COL].values - 1]
    b_arr = get_B(st=st_df, u=u_arr, v=v_arr, k=k)
    i = 0
    previous_rmse = sys.maxint
    current_rmse = previous_rmse - 1 - epsilon
    while i < t and previous_rmse - current_rmse > epsilon:
        u_arr = update_u(k=k, num_of_users=len(u_arr), st=st_df, b=b_arr)
        st_df[USER_CLUSTER_ID_COL] = u_arr[st_df[USER_ID_COL].values - 1]
        b_arr = get_B(st=st_df, u=u_arr, v=v_arr, k=k)
        v_arr = update_v(k=k, num_of_movies=len(v_arr), st=st_df, b=b_arr)
        st_df[MOVIE_CLUSTER_ID_COL] = v_arr[st_df[MOVIE_ID_COL].values - 1]
        b_arr = get_B(st=st_df, u=u_arr, v=v_arr, k=k)
        previous_rmse = current_rmse
        current_rmse = get_rmse(sv=sv_df, b=b_arr, u=u_arr, v=v_arr)
        i += 1
    np.savetxt(u_path, u_arr, delimiter=',')
    np.savetxt(v_path, v_arr, delimiter=',')
    np.savetxt(b_path, b_arr, delimiter=',')


def get_codebook_recoms(user_id, n):
    u_arr = np.loadtxt(u_path, delimiter=',')
    v_arr = np.loadtxt(v_path, delimiter=',')
    b_arr = np.loadtxt(b_path, delimiter=',')
    user_cluster = int(u_arr[user_id - 1])
    movie_clusters = b_arr[user_cluster]
    # sort cluster indices by descending ranking (best matching cluster first)
    cluster_indices = np.argsort(movie_clusters)[::-1]
    recoms = []
    for c_id in cluster_indices:
        # get indices (IDs) of all movies that belong to 'c_id' cluster
        movie_ids = np.flatnonzero(v_arr == c_id)
        # choose first 10 movies in the cluster (random)
        recoms += list(movie_ids[:n])
        if len(recoms) == n:
            break
    return recoms


@app.route('/', methods=['POST'])
def get_recommendation():
    try:
        data = json.loads(request.data)
        assert 'n' in data, "Missing number of recommendations"
        assert 'userid' in data, "Missing user ID"
        n = int(data['n'])
        user_id = int(data['userid'])
        recoms = get_codebook_recoms(user_id, n)
        return jsonify(recoms)
    except Exception as e:
        return repr(e), 500


if __name__ == '__main__':
    try:
        # pd.set_option('mode.chained_assignment', None)
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
        # global u_path, v_path, b_path
        # u_path = sys.argv[6] + r"u.csv"
        # v_path = sys.argv[7] + r"v.csv"
        # b_path = sys.argv[8] + r"b.csv"

        # build_b_file()

        app.run()
    except Exception as ex:
        print "Error!", ex
        print traceback.print_exc()
