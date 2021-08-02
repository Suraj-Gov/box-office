from controller import verify_login
from tkinter import *
from windows import *
from theme import *
from components import *
from filenames import *
from utils import *

app = Tk()
app.resizable(False, False)
app.withdraw()

state = {"user": {"name": None}}

active_window = None


def add_update_movie():
    global app
    render_add_update_movies_window(app)


def login_user(username_field, password_field):
    global app
    global active_window
    is_authenticated = verify_login(
        state, username_field, password_field)
    if is_authenticated:
        active_window = render_view_movies_window(
            app, active_window)


def login_signup():
    username_str_var = StringVar()
    password_str_var = StringVar()
    global app
    global active_window
    active_window = render_login_signup_window(app, active_window, username_str_var, password_str_var, lambda: login_user(
        username_str_var.get(), password_str_var.get()))


def start():
    global app, active_window
    active_window = render_start_window(app, active_window, login_signup, None)


render_view_movies_window(app, active_window)
# TODO change to start()
# start()

app.mainloop()
