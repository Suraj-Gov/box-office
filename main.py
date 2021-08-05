from controller import verify_login
from tkinter import *
from windows import *
from theme import *
from components import *
from filenames import *
from utils import *
import state

app = Tk()
app.resizable(False, False)
app.withdraw()


active_window = None


def add_update_movie():
    global app
    render_add_update_movies_window(app)


def login_user(username_field: StringVar, password_field: StringVar):
    global app
    global active_window
    is_authenticated = verify_login(username_field, password_field)
    if is_authenticated:
        state.user = is_authenticated
        state.role = "CRITIC"
        active_window = render_view_movies_window(app, active_window)
    else:
        messagebox.showerror(message="The credentials do not match, please try again.")


def login_signup():
    username_str_var = StringVar()
    password_str_var = StringVar()
    global app
    global active_window
    active_window = render_login_signup_window(
        app,
        active_window,
        username_str_var,
        password_str_var,
        lambda: login_user(username_str_var.get(), password_str_var.get()),
    )


def start():
    global app, active_window
    active_window = render_start_window(app, active_window, login_signup, None)


# render_view_movies_window(app, active_window)
# TODO change to start()
start()

app.mainloop()
