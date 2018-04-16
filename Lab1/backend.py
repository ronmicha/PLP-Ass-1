import os
import sys
import csv
import sqlite3
from flask import Flask, jsonify, request

db_path = "sqlite_db.db"
movies_path = "movies.csv"
ratings_path = "ratings.csv"

app = Flask(__name__)


# region Part A
def create_movies_table():
    if not os.path.isfile(db_path):
        with sqlite3.connect(db_path) as connection:
            connection.text_factory = str
            cursor = connection.cursor()
            sql_command = "CREATE TABLE IF NOT EXISTS movies (ID INTEGER PRIMARY KEY, Title TEXT, Genre TEXT)"
            cursor.execute(sql_command)
            connection.commit()
            with open(movies_path, "r") as movies_file:
                reader = csv.reader(movies_file)
                next(reader)  # skip header row
                movies_list = []
                for row in reader:
                    movie_id = row[0]
                    title = row[1]
                    genre = row[2].split("|")[0].strip()
                    movies_list.append((movie_id, title, genre))
            sql_command = "INSERT INTO movies (ID, Title, Genre) " \
                          "VALUES (?, ?, ?)"
            cursor.executemany(sql_command, movies_list)
            connection.commit()


def get_all_movies():
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "SELECT * " \
                      "FROM movies " \
                      "ORDER BY Title"
        cursor.execute(sql_command)
        all_movies = convert_cursor_to_list(cursor)
    return all_movies


def search_movies(movie_id, title, genre):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "SELECT * " \
                      "FROM movies " \
                      "WHERE ID = {0} AND Title = {1} AND Genre = {2} " \
                      "ORDER BY Title".format(movie_id, title, genre)
        cursor.execute(sql_command)
        movies = convert_cursor_to_list(cursor)
    return movies


def add_movie(movie_id, title, genre):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "INSERT INTO movies " \
                      "VALUES (?, ?, ?)"
        cursor.execute(sql_command, (movie_id, title, genre))


def update_movie(old_movie_id, new_movie_id, new_title, new_genre):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "UPDATE movies " \
                      "SET ID = ?, Title = ?, Genre = ? " \
                      "WHERE ID = ?"
        cursor.execute(sql_command, (new_movie_id, new_title, new_genre, old_movie_id))


def delete_movie(movie_id):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "DELETE FROM movies " \
                      "WHERE ID = ?"
        cursor.execute(sql_command, (movie_id,))


def convert_cursor_to_list(cursor):
    lst = []
    for row in cursor.fetchall():
        row_list = list(row)
        row_list[0] = str(row_list[0])
        lst.append(" | ".join(row_list))
    return lst


# endregion

# region Part B
def create_ratings_table():
    create_movies_table()
    with sqlite3.connect(db_path) as connection:
        connection.text_factory = str
        cursor = connection.cursor()
        statement = "SELECT name " \
                    "FROM sqlite_master " \
                    "WHERE type='table' AND name = ?"
        if cursor.execute(statement, ("ratings",)).fetchall():
            return
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
    try:
        if request.method == 'POST':
            user_id = None if 'userid' not in request.form else request.form['userid']
            k = None if 'k' not in request.form else request.form['k']
        else:
            user_id = request.args.get('userid')
            k = request.args.get('k')
        if not k or not user_id:
            raise Exception("Missing k or userid")
        try:
            k = int(k)
            user_id = int(user_id)
        except ValueError:
            raise Exception("Wrong parameters. userid and k must be integers.")
        assert k > 0, "K must be positive"
        return jsonify(get_user_recommendation(int(user_id), int(k)))
    except Exception as ex:
        return ex.message, 500


def get_user_recommendation(user_id, k):
    create_ratings_table()
    related_users = get_related_users(user_id)
    similarities = []  # list of tuples (user_id, similarity)
    for related_user_id in related_users:
        related_user_similarity = get_similarity(user_id, related_user_id)
        similarities.append(related_user_similarity)
    # sort list by similarity desc
    similarities.sort(key=lambda sim_tuple: sim_tuple[1], reverse=True)
    recommended_movies_ids = get_recommended_movies_ids(user_id, similarities, k)
    id_to_title_dict = get_id_to_title_dict(recommended_movies_ids)
    recommended_movies = [id_to_title_dict[movie_id] for movie_id in recommended_movies_ids]
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


def get_recommended_movies_ids(user_id, similarities, k):
    recommended_movies_ids = []
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        user_movies_ids_sql_command = "SELECT MOVIE_ID " \
                                      "FROM ratings " \
                                      "WHERE USER_ID = ?"
        cursor.execute(user_movies_ids_sql_command, (user_id,))
        user_movies_ids = set(cursor.fetchall())
        sql_command = "SELECT MOVIE_ID " \
                      "FROM ratings " \
                      "WHERE USER_ID = ? " \
                      "ORDER BY RATING DESC"
        for similarity in similarities:
            user_id = similarity[0]
            cursor.execute(sql_command, (user_id,))
            movie_id = cursor.fetchone()[0]
            while movie_id in recommended_movies_ids or movie_id in user_movies_ids:
                movie_id = cursor.fetchone()[0]
            recommended_movies_ids.append(movie_id)
            if len(recommended_movies_ids) == k:
                break
    return recommended_movies_ids


def get_id_to_title_dict(movies_ids):
    movies_ids = ", ".join(str(movie_id) for movie_id in movies_ids)
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "SELECT DISTINCT ID, Title " \
                      "FROM movies " \
                      "WHERE ID IN ({0})".format(movies_ids)
        cursor.execute(sql_command)
        return dict(cursor.fetchall())


# endregion

if __name__ == '__main__':
    app.run()
