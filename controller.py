from tkinter.constants import END, X
from typing import List
from filenames import *
from tkinter import Listbox, Scrollbar, Toplevel, messagebox
from utils import *


def verify_login(username: str, password: str):
    """provide state map, username_field, password_field, returns username for successful login"""
    does_user_exist = check_key_exist(username, USER_INDEX_FILE)
    if does_user_exist:
        user_data = get_record(username, USER_INDEX_FILE, USER_DATA_FILE)
        _, hash_str = user_data.split("|")
        is_authenticated = verify_password(password, hash_str)
        if is_authenticated:
            messagebox.showinfo(message="You are authorized!")
            return username
        else:
            messagebox.showerror(
                message="You are not authorized. \nPlease check your password"
            )
    else:
        does_want_to_sign_up = messagebox.askyesno(
            message="A user does not exist.\nDo you want to create a new user with this credentials?",
        )
        if does_want_to_sign_up:
            user_signup_success = create_record(
                USER_DATA_FILE,
                USER_INDEX_FILE,
                username,
                f"{username}|{get_password_hash(password)}",
            )
            if user_signup_success:
                messagebox.showinfo(
                    message="Signed up successfully.\nPlease login again"
                )
                return "LOGIN_AGAIN"
            else:
                messagebox.showerror(
                    message="Something went wrong when signing up.\nPlease check the logs",
                )
                return False
        else:
            return False


def add_update_movie(movie_title: str):
    """provide a movie_title
    if movie title exists in record, it returns unpadded movie_record
    if movie title not exist in record,
    returns True if user wants to add the movie
    else returns False"""
    movie_record = get_record(movie_title, MOVIE_INDEX_FILE, MOVIE_DATA_FILE)
    if not movie_record:
        does_want_to_add_movie = messagebox.askokcancel(
            message="Movie doesn't exist.\nDo you want to add the movie?"
        )
        if does_want_to_add_movie:
            return True
        else:
            return False
    else:
        return movie_record.strip()


def add_update_movie_record(
    title: str, director: str, cast: str, about: str, rating: str, opt: str
):
    """provide movie details, opt = "ADD" | "UPDATE"
    returns True if inserted successfully, else False"""
    title = title.strip().replace("|", "")
    director = director.strip().replace("|", "")
    cast = cast.strip().replace("|", "")
    about = about.strip().replace("|", "")
    if title == "" or director == "" or cast == "" or about == "":
        messagebox.showerror(message="Make sure all fields have some valid value.")
        return False
    data = f"{title}|{director}|{cast}|{about}|{rating}"
    if opt == "ADD":
        create_record(MOVIE_DATA_FILE, MOVIE_INDEX_FILE, title, data)
    elif opt == "UPDATE":
        update_record(
            MOVIE_DATA_FILE, MOVIE_INDEX_FILE, title, data.ljust(RECORD_LENGTH)
        )
    return True


def load_movies(movies_list: Listbox, movie_data: List[str], window: Toplevel):
    movies_list.delete(0, movies_list.size() - 1)
    movie_data.clear()
    movie_data.extend(get_all_records(MOVIE_INDEX_FILE))
    for movie_record_str in movie_data:
        movie_title = movie_record_str.split("|")[0]
        movies_list.insert(END, movie_title)


def search_movies(movies_list: Listbox, movie_data: List[str], search_str: str):
    """searches for movies with the given search_str"""
    if movies_list is None:
        return
    movies_list.delete(0, movies_list.size() - 1)
    movie_data.clear()
    movie_idxs = get_all_records(MOVIE_INDEX_FILE)
    if movie_idxs == False:
        return
    for movie in movie_idxs:
        title, _ = movie.split("|")
        if title.lower().find(search_str) >= 0:
            movie_data.append(movie)
    for movie_record_str in movie_data:
        title, _ = movie_record_str.split("|")
        movies_list.insert(END, title)
