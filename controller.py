from filenames import *
from tkinter import messagebox
from utils import *


def verify_login(username, password):
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
                return False
            else:
                messagebox.showerror(
                    message="Something went wrong when signing up.\nPlease check the logs",
                )
                return False
        else:
            return False


def add_update_movie(movie_title):
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


def add_update_movie_record(title: str, director: str, cast: str, about: str, opt: str):
    """provide movie details, opt = "ADD" | "UPDATE"
    returns True if inserted successfully, else False"""
    title = title.replace("|", "")
    director = director.replace("|", "")
    cast = cast.replace("|", "")
    about = about.replace("|", "")
    data = f"{title}|{director}|{cast}|{about}"
    if opt == "ADD":
        create_record(MOVIE_DATA_FILE, MOVIE_INDEX_FILE, title, data)
    elif opt == "UPDATE":
        update_record(
            MOVIE_DATA_FILE, MOVIE_INDEX_FILE, title, data.ljust(RECORD_LENGTH)
        )
    return True
