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


# ratings_path = "./ratings.csv"
# u_path = "\\"
# v_path = "\\"
# b_path = "\\"


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
        user_data = st[st[USER_ID_COL] == user_id]
        user_ratings_arr = user_data[RATING_COL].values
        movies_clusters_arr = user_data[MOVIE_CLUSTER_ID_COL].values
        for user_cluster_id in range(k):
            error_series = (user_ratings_arr - b[user_cluster_id, movies_clusters_arr]) ** 2
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
        movie_data = st[st[MOVIE_ID_COL] == movie_id]
        movie_ratings_arr = movie_data[RATING_COL].values
        user_cluster_arr = movie_data[USER_CLUSTER_ID_COL].values
        for movie_cluster_id in range(k):
            errors_series = (movie_ratings_arr - b[user_cluster_arr, movie_cluster_id]) ** 2
            if len(errors_series) == 0:
                break
            error = errors_series.sum()
            if error < min_error:
                min_error = error
                min_cluster = movie_cluster_id
        v[movie_id - 1] = min_cluster
    return v.astype('int32')


def get_rmse(sv, b, u, v):
    mse = ((sv[RATING_COL].values - b[u[sv[USER_ID_COL].values], v[sv[MOVIE_ID_COL].values]]) ** 2).mean()
    return mse ** 0.5


def build_b_file(ratings_path, k=20, t=10, epsilon=0.01):
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


@app.before_first_request
def load_files():
    global u_rec, v_rec, b_rec, ratings
    u_rec = np.loadtxt(u_path, delimiter=',')
    v_rec = np.loadtxt(v_path, delimiter=',')
    b_rec = np.loadtxt(b_path, delimiter=',')
    ratings = pd.read_csv(ratings_path)


def get_codebook_recoms(user_id, n):
    user_cluster = int(u_rec[user_id - 1])
    movie_clusters = b_rec[user_cluster]
    movies_watched = ratings[ratings[USER_ID_COL] == user_id][MOVIE_ID_COL].values
    # get cluster indices (IDs) by descending ranking (best cluster ID first)
    cluster_ids = np.argsort(movie_clusters)[::-1]
    recoms = []
    for c_id in cluster_ids:
        # get indices (IDs) of all movies that belong to 'c_id' cluster
        movie_ids = np.flatnonzero(v_rec == c_id) + 1
        potential_recoms = np.setdiff1d(movie_ids, movies_watched)
        # choose first movies in the cluster (random)
        recoms += list(potential_recoms[:n - len(recoms)])
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
        pd.set_option('mode.chained_assignment', None)
        assert len(sys.argv) == 9, "Wrong number of arguments. Please provide 8 arguments"
        assert sys.argv[1] == 'ExtractCB', "Wrong method provided. Method must be ExtractCB"
        assert os.path.basename(sys.argv[2]) == "ratings.csv", "Wrong input file provided. Input file must be named 'ratings.csv'"
        assert os.path.isfile(sys.argv[2]), "Input file path is invalid or file doesn't exist"

        try:
            if not isinstance(eval(sys.argv[3]), int):
                raise Exception
        except Exception as ex:
            raise Exception("K must be an integer")

        try:
            if sys.argv[4] and not isinstance(eval(sys.argv[4]), int):
                raise Exception
        except Exception as ex:
            raise Exception("T must be either empty or an integer")

        try:
            if sys.argv[5] and not isinstance(eval(sys.argv[5]), float):
                raise Exception
        except Exception as ex:
            raise Exception("Epsilon must be either empty or a decimal number")

        assert not sys.argv[6] or os.path.isdir(sys.argv[6]), "U directory is invalid or doesn't exist"
        assert not sys.argv[7] or os.path.isdir(sys.argv[7]), "V directory is invalid or doesn't exist"
        assert not sys.argv[8] or os.path.isdir(sys.argv[8]), "B directory is invalid or doesn't exist"

        ratings_path = sys.argv[2]
        k_size = int(sys.argv[3])
        t_size = 10 if not sys.argv[4] else int(sys.argv[4])
        epsilon = 0.01 if not sys.argv[5] else float(sys.argv[5])
        u_path = sys.argv[6] + "\\u.csv" if sys.argv[6] else "u.csv"
        v_path = sys.argv[7] + "\\v.csv" if sys.argv[7] else "v.csv"
        b_path = sys.argv[8] + "\\b.csv" if sys.argv[8] else "b.csv"

        # build_b_file(ratings_path=ratings_path, k=k_size, t=t_size, epsilon=epsilon)

        print "Recommendation service is ready to receive requests..."
        app.run()
    except Exception as ex:
        print "ERROR!", ex
        # print traceback.print_exc()
