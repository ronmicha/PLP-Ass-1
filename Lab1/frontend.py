import backend
from Tkinter import *


def get_all_movies():
    # TODO: display just the movie names or the whole data? Whole data requires using TkTreectrl (multi-column listbox) which we didn't learn
    all_movies = backend.get_all_movies()
    fill_listbox(all_movies)


def search_movies(movie_id, title, genre):
    movies = backend.search_movies(movie_id.get(), title.get(), genre.get())
    fill_listbox(movies)


def add_movie(movie_id, title, genre):
    backend.add_movie(movie_id.get(), title.get(), genre.get())


def update_movie(new_movie_id, new_title, new_genre):
    x = movies_listbox.curselection()
    backend.update_movie(new_movie_id.get(), new_title.get(), new_genre.get())


def delete_movie(movie_id):
    backend.delete_movie(movie_id.get())


def close():
    pass


def fill_listbox(values):
    movies_listbox.delete(0, END)  # clear listbox
    for value in values:
        movies_listbox.insert(END, value)


backend.create_table()

# region Tkinter GUI
window = Tk()

title_var = StringVar()
id_var = IntVar()
genre_var = StringVar()

title_label = Label(window, text="Title")
id_label = Label(window, text="ID")
genre_label = Label(window, text="Genre")

title_entry = Entry(window, textvariable=title_var)
id_entry = Entry(window, textvariable=id_var)
genre_entry = Entry(window, textvariable=genre_var)

scrollbar = Scrollbar(window, orient=VERTICAL)
movies_listbox = Listbox(window, selectmode=SINGLE, yscrollcommand=scrollbar.set)
scrollbar.config(command=movies_listbox.yview)

view_all_button = Button(window, text="View all", command=lambda: get_all_movies())
search_button = Button(window, text="Search entry", command=lambda: search_movies(id_var, title_var, genre_var))
add_button = Button(window, text="Add entry", command=lambda: add_movie(id_var, title_var, genre_var))
update_button = Button(window, text="Update selected", command=lambda: update_movie(id_var, title_var, genre_var))
delete_button = Button(window, text="Delete selected", command=lambda: delete_movie(id_var))
close_button = Button(window, text="Close", command=close)

title_label.grid(row=0, column=1)
title_entry.grid(row=0, column=2)
id_label.grid(row=1, column=1)
id_entry.grid(row=1, column=2)
genre_label.grid(row=0, column=3)
genre_entry.grid(row=0, column=4)
movies_listbox.grid(row=3, column=0, columnspan=3)
scrollbar.grid(row=4, column=3)
view_all_button.grid(row=2, column=4)
search_button.grid(row=3, column=4)
add_button.grid(row=4, column=4)
update_button.grid(row=5, column=4)
delete_button.grid(row=6, column=4)
close_button.grid(row=7, column=4)

window.mainloop()
# endregion
