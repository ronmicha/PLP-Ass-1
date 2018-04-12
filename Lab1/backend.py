import os
import sqlite3
from flask import Flask
from flask import jsonify
from flask import request

db_path = "sqlite_db.db"
movies_path = "movies.csv"
ratings_path = "ratings.csv"

app = Flask(__name__)


def create_table():
    if not os.path.isfile(db_path):
        with sqlite3.connect(db_path) as connection:
            connection.text_factory = str
            cursor = connection.cursor()
            sql_command = "CREATE TABLE IF NOT EXISTS movies (ID INTEGER PRIMARY KEY, Title TEXT, Genre TEXT)"
            cursor.execute(sql_command)
            connection.commit()
            with open(movies_path, "r") as movies_file:
                next(movies_file)  # skip header row
                movies_list = []
                for row in movies_file:
                    try:  # TODO: Some rows have comma in "movieId" column. Ask Nahmias
                        movie_id, title, genre = row.strip().split(",")
                        title = title.split("(")[0].strip()
                        genre = genre.split("|")[0].strip()
                        movies_list.append((movie_id, title, genre))
                    except:
                        pass
            sql_command = "INSERT INTO movies (ID, Title, Genre) VALUES (?, ?, ?)"
            cursor.executemany(sql_command, movies_list)
            connection.commit()


def get_all_movies():
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        sql_command = "SELECT Title FROM movies ORDER BY Title"
        cursor.execute(sql_command)
        all_movies = [title_tuple[0] for title_tuple in cursor.fetchall()]
    return all_movies


def search_movies(movie_id, title, genre):
    pass


def add_movie(movie_id, title, genre):
    pass


def update_movie(movie_id, title, genre):
    pass


def delete_movie(movie_id):
    pass
