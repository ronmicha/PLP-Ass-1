import backend
from Tkinter import *
from tkMessageBox import *


def get_all_movies():
    all_movies = backend.get_all_movies()
    fill_listbox(all_movies)


def search_movies(movie_id, title, genre):
    movie_id = "ID" if not movie_id.get() else movie_id.get()
    title = "Title" if not title.get() else "'{}'".format(title.get())
    genre = "Genre" if not genre.get() else "'{}'".format(genre.get())
    movies = backend.search_movies(movie_id, title, genre)
    fill_listbox(movies)


def add_movie(movie_id, title, genre):
    movie_id = movie_id.get()
    title = title.get()
    genre = genre.get()
    if not movie_id or not title or not genre:
        showerror("Error - Missing Values", "Please fill \"Title\", \"ID\", \"Genre\" fields and try again.")
        return
    backend.add_movie(movie_id, title, genre)


def update_movie(new_movie_id, new_title, new_genre):
    backend.update_movie(new_movie_id.get(), new_title.get(), new_genre.get())


def delete_movie(movie_id):
    backend.delete_movie(movie_id.get())


def close():
    window.destroy()


def fill_listbox(values):
    movies_listbox.delete(0, END)  # clear listbox
    for value in values:
        movies_listbox.insert(END, value)


def movies_listbox_on_select(evt):
    selected_item_index = movies_listbox.curselection()
    selected_item = movies_listbox.get(selected_item_index)
    movie_id, title, genre = selected_item.split(" | ")
    id_var.set(movie_id)
    title_var.set(title)
    genre_var.set(genre)


backend.create_movies_table()

# region Tkinter GUI
window = Tk()
window.geometry("500x300")

title_var = StringVar()
id_var = StringVar()
genre_var = StringVar()

title_label = Label(window, text="Title")
id_label = Label(window, text="ID")
genre_label = Label(window, text="Genre")

title_entry = Entry(window, textvariable=title_var)
id_entry = Entry(window, textvariable=id_var)
genre_entry = Entry(window, textvariable=genre_var)

scrollbar = Scrollbar(window, orient=VERTICAL)
movies_listbox = Listbox(window, selectmode=SINGLE, yscrollcommand=scrollbar.set)
movies_listbox.bind("<<ListboxSelect>>", movies_listbox_on_select)
scrollbar.config(command=movies_listbox.yview)

view_all_button = Button(window, text="View all", command=lambda: get_all_movies())
search_button = Button(window, text="Search entry", command=lambda: search_movies(id_var, title_var, genre_var))
add_button = Button(window, text="Add entry", command=lambda: add_movie(id_var, title_var, genre_var))
update_button = Button(window, text="Update selected", command=lambda: update_movie(id_var, title_var, genre_var))
delete_button = Button(window, text="Delete selected", command=lambda: delete_movie(id_var))
close_button = Button(window, text="Close", command=close)

num_of_rows = 10
num_of_columns = 15

for i in range(num_of_rows):
    window.rowconfigure(i, weight=1)
for i in range(num_of_columns):
    window.columnconfigure(i, weight=1)

button_column = 12

title_label.grid(row=0, column=2)
title_entry.grid(row=0, column=3, sticky="EW")
id_label.grid(row=1, column=2)
id_entry.grid(row=1, column=3, sticky="EW")
genre_label.grid(row=0, column=8)
genre_entry.grid(row=0, column=9, sticky="EW")
movies_listbox.grid(row=3, column=0, columnspan=10, rowspan=4, sticky="NESW")
scrollbar.grid(row=3, column=10, rowspan=4, sticky="NS")
view_all_button.grid(row=2, column=button_column, sticky="EW", padx=(10, 10))
search_button.grid(row=3, column=button_column, sticky="EW", padx=(10, 10))
add_button.grid(row=4, column=button_column, sticky="EW", padx=(10, 10))
update_button.grid(row=5, column=button_column, sticky="EW", padx=(10, 10))
delete_button.grid(row=6, column=button_column, sticky="EW", padx=(10, 10))
close_button.grid(row=7, column=button_column, sticky="EW", padx=(10, 10))

window.mainloop()
# endregion
