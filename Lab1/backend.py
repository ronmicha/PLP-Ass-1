import os
from itertools import groupby
from operator import itemgetter
import csv
import math
import sqlite3
from flask import Flask, jsonify, request

db_path = "sqlite_db.db"
movies_path = "movies.csv"
ratings_path = "ratings.csv"

app = Flask(__name__)


# region Part A
def create_movies_table():
    if not os.path.isfile(db_path):  # ToDo what if the file already exists but the table isnt?
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
        all_movies = []
        for row in cursor.fetchall():
            row_list = list(row)
            row_list[0] = str(row_list[0])
            all_movies.append(" | ".join(row_list))
    return all_movies


def search_movies(movie_id, title, genre):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "SELECT * " \
                      "FROM movies " \
                      "WHERE ID = {0} AND Title = {1} AND Genre = {2} " \
                      "ORDER BY Title".format(movie_id, title, genre)
        cursor.execute(sql_command)
        movies = []
        for row in cursor.fetchall():
            row_list = list(row)
            row_list[0] = str(row_list[0])
            movies.append(" | ".join(row_list))
    return movies


def add_movie(movie_id, title, genre):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "INSERT INTO movies " \
                      "VALUES (?, ?, ?)"
        cursor.execute(sql_command, (movie_id, title, genre))


def update_movie(movie_id, title, genre):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "UPDATE movies " \
                      "SET ID = ?, Title = ?, Genre = ? " \
                      "WHERE ID = ?"
        cursor.execute(sql_command, (movie_id, title, genre, movie_id))


def delete_movie(movie_id):
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "DELETE FROM movies " \
                      "WHERE ID = ?"
        cursor.execute(sql_command, (movie_id,))


# endregion

# region Part B
def create_rating_table():
    with sqlite3.connect(db_path) as connection:
        connection.text_factory = str
        cursor = connection.cursor()
        statement = "SELECT name FROM sqlite_master WHERE type='table';"
        if ('ratings',) in cursor.execute(statement).fetchall():
            return
        sql_command = "CREATE TABLE IF NOT EXISTS ratings (userId INTEGER ,movieId INTEGER," \
                      " rating FLOAT, timestamp TIMESTAMP)"
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
                timestamp = row[3]
                ratings_list.append((user_id, movie_id, rating, timestamp))
        sql_command = "INSERT INTO ratings (userID, movieID, rating, timestamp) " \
                      "VALUES (?, ?, ?, ?)"
        cursor.executemany(sql_command, ratings_list)
        connection.commit()


def select(query):
    result = []
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
    return result


def get_recommendation(userid, k):
    create_rating_table()
    user_avg_q = "SELECT movieID, rating " \
                 "FROM ratings " \
                 "WHERE userID = {0} ".format(userid)
    given_user_ratings = dict(select(user_avg_q))
    given_user_avg = sum(given_user_ratings.values()) / len(given_user_ratings)
    users_id_q = "SELECT userID, movieID, rating  " \
                 "FROM ratings " \
                 "WHERE userID <> {0} AND " \
                 "movieID in (SELECT movieID FROM ratings WHERE userID ={0}) " \
                 "GROUP BY userID, movieID ".format(userid)
    # Create collection with following format:
    # [ userID, {movieID: rating, movieID: rating}]
    users_ratings = [[user[0], [user[1], user[2]]] for user in select(users_id_q)]
    users_ratings = {k: dict(list(zip(*g))[1]) for k, g in groupby(users_ratings, itemgetter(0))}
    distances = {}
    for user in users_ratings:
        current_user_ratings = users_ratings[user]
        current_user_avg = sum(current_user_ratings.values()) / len(current_user_ratings)
        mutual_movies = [movieId for movieId in given_user_ratings if movieId in current_user_ratings]
        numerator = sum(
            [(given_user_ratings[movieId] - given_user_avg) * (current_user_ratings[movieId] - current_user_avg)
             for movieId in mutual_movies])
        denominator_left = sum(
            [math.pow(given_user_ratings[movieId] - given_user_avg, 2) for movieId in mutual_movies])
        denominator_right = sum(
            [math.pow(current_user_ratings[movieId] - current_user_avg, 2) for movieId in mutual_movies])
        if denominator_left == 0 or denominator_right == 0:
            score = 0
        else:
            score = numerator / (denominator_left * denominator_right)
        distances[user] = score
    sorted_users = sorted(distances, key=distances.get, reverse=True)

    recs_ids = []
    for i in range(0, min(k, len(sorted_users) - 1)):
        movies = users_ratings[sorted_users[i]]
        movies_sorted = sorted(movies, key=movies.get, reverse=True)
        for movie in movies_sorted:
            if movie not in recs_ids:
                recs_ids.append(movie)
                break
    movies_as_list = ", ".join(str(rec) for rec in recs_ids)
    movies_query = "SELECT ID, Title " \
                   "FROM movies " \
                   "WHERE ID in ({0})".format(movies_as_list)
    id_to_title = dict(select(movies_query))
    return [id_to_title[id] for id in recs_ids]


@app.route('/rec', methods=['GET', 'POST'])
def rec():
    try:
        if request.method == 'POST':
            userid = None if 'userid' not in request.form else request.form['userid']
            k = None if 'k' not in request.form else request.form['k']
        elif request.method == 'GET':
            userid = request.args.get('userid')
            k = request.args.get('k')
        if not k or not userid:
            raise Exception("Missing k or userid")
        return jsonify(get_recommendation(int(userid), int(k)))
    except Exception as ex:
        return ex.message, 500


# endregion
if __name__ == '__main__':
    app.run()
