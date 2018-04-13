import os
import csv
import sqlite3
from flask import Flask, jsonify, request

db_path = "sqlite_db.db"
movies_path = "movies.csv"
ratings_path = "ratings.csv"

app = Flask(__name__)


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
