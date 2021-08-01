from filenames import *
from tkinter import messagebox
from utils import *


def verify_login(state, username, password):
    """provide state map, username_field, password_field, returns True for successful login"""
    does_user_exist = check_key_exist(username, USER_INDEX_FILE)
    if does_user_exist:
        user_data = get_record(username, USER_INDEX_FILE, USER_DATA_FILE)
        _, hash_str = user_data.split("|")
        is_authenticated = verify_password(password, hash_str)
        if is_authenticated:
            messagebox.showinfo(message="You are authorized!")
            state["user"] = username
            return True
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
