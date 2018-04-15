import sys
import csv
import sqlite3
from flask import Flask
from flask import request
from flask import jsonify

db_path = "sqlite_db.db"
ratings_path = "ratings.csv"

app = Flask(__name__)


def create_ratings_table():
    with sqlite3.connect(db_path) as connection:
        connection.text_factory = str
        cursor = connection.cursor()
        sql_command = "CREATE TABLE IF NOT EXISTS ratings (USER_ID INTEGER, MOVIE_ID INTEGER, RATING REAL, TS TEXT, " \
                      "PRIMARY KEY (USER_ID, MOVIE_ID))"
        cursor.execute(sql_command)
        connection.commit()
        with open(ratings_path, "r") as ratings_file:
            reader = csv.reader(ratings_file)
            next(reader)  # skip header row
            ratings_list = []
            for row in reader:
                user_id = row[0]
                movie_id = row[1]
                rating = row[2]
                ts = row[3]
                ratings_list.append((user_id, movie_id, rating, ts))
        sql_command = "INSERT INTO ratings (USER_ID, MOVIE_ID, RATING, TS) " \
                      "VALUES (?, ?, ?, ?)"
        cursor.executemany(sql_command, ratings_list)
        connection.commit()


@app.route('/rec', methods=['GET', 'POST'])
def rec():
    if request.method == "GET":
        if len(request.args) != 2:
            return "Bad request. Please provide 'userid' and 'k'", 400
        user_id = request.args["userid"]
        k = request.args["k"]

    else:  # request.method == "POST"
        if len(request.data) != 2:
            return "Bad request. Please provide 'userid' and 'k'", 400
        user_id = request.data["userid"]
        k = request.data["k"]

    if not user_id or not k:
        return "Bad request. 'userid' and 'k' must have values", 400

    return jsonify(get_user_recommendation(int(user_id), int(k))), 200


def get_user_recommendation(user_id, k):
    related_users = get_related_users(user_id)
    similarities = []  # list of tuples (user_id, similarity)
    for related_user_id in related_users:
        related_user_similarity = get_similarity(user_id, related_user_id)
        similarities.append(related_user_similarity)
    # sort list by similarity desc
    similarities.sort(key=lambda sim_tuple: sim_tuple[1], reverse=True)
    recommended_movies_ids = get_recommended_movies_ids(similarities, k)
    recommended_movies = get_movies_names(recommended_movies_ids)
    return recommended_movies


def get_related_users(user_id):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        inner_sql_command = "SELECT MOVIE_ID " \
                            "FROM ratings " \
                            "WHERE USER_ID = ?"
        sql_command = "SELECT DISTINCT USER_ID " \
                      "FROM ratings " \
                      "WHERE USER_ID <> ? AND MOVIE_ID IN ({0})".format(inner_sql_command)
        cursor.execute(sql_command, (user_id, user_id))
        return [row[0] for row in cursor.fetchall()]


def get_similarity(user_id_1, user_id_2):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        avg_rating_sql_command = "SELECT AVG(RATING) " \
                                 "FROM ratings " \
                                 "WHERE USER_ID IN (?, ?) " \
                                 "GROUP BY USER_ID"
        cursor.execute(avg_rating_sql_command, (user_id_1, user_id_2))
        user_1_avg_rating = cursor.fetchone()[0]
        user_2_avg_rating = cursor.fetchone()[0]
        sql_command = "SELECT * " \
                      "FROM ratings r1 INNER JOIN ratings r2 " \
                      "ON r1.MOVIE_ID = r2.MOVIE_ID " \
                      "WHERE r1.USER_ID = ? AND r2.USER_ID = ?"
        cursor.execute(sql_command, (user_id_1, user_id_2))
        joint_movies = [row for row in cursor.fetchall()]

    numerator = denominator_left = denominator_right = 0
    for row in joint_movies:
        user_1_rating = row[2]
        user_2_rating = row[6]
        numerator += (user_1_rating - user_1_avg_rating) * (user_2_rating - user_2_avg_rating)
        denominator_left += (user_1_rating - user_1_avg_rating) ** 2
        denominator_right += (user_2_rating - user_2_avg_rating) ** 2

    if denominator_left == 0:
        denominator_left += sys.float_info.epsilon
    if denominator_right == 0:
        denominator_right += sys.float_info.epsilon
    denominator_left = denominator_left ** 0.5
    denominator_right = denominator_right ** 0.5
    similarity = numerator / (denominator_left * denominator_right)
    return user_id_2, similarity


def get_recommended_movies_ids(similarities, k):
    recommended_movies_ids = set()
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "SELECT MOVIE_ID " \
                      "FROM ratings " \
                      "WHERE USER_ID = ? " \
                      "ORDER BY RATING DESC"
        for similarity in similarities:
            user_id = similarity[0]
            cursor.execute(sql_command, (user_id,))
            movie_id = cursor.fetchone()[0]
            while movie_id in recommended_movies_ids:
                movie_id = cursor.fetchone()[0]
            recommended_movies_ids.add(movie_id)
            if len(recommended_movies_ids) == k:
                break
    return recommended_movies_ids


def get_movies_names(movies_ids):
    movies_ids = ", ".join(str(movie_id) for movie_id in movies_ids)
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "SELECT DISTINCT Title " \
                      "FROM movies " \
                      "WHERE ID IN ({0})".format(movies_ids)
        cursor.execute(sql_command)
        return [row[0] for row in cursor.fetchall()]


if __name__ == '__main__':
    # create_ratings_table()
    app.run()
