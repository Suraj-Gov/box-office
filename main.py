from tkinter import *
from tkinter import messagebox
from theme import *
from components import *
from filenames import *
from utils import *

app = Tk()
app.resizable(False, False)
app.withdraw()

state = {"user": {"name": None}}

active_window = None


def login_user(username_field, password_field):
    global app
    global active_window
    username = username_field.get()
    password = password_field.get()
    does_user_exist = check_key_exist(username, USER_INDEX_FILE)
    if does_user_exist:
        user_data = get_record(username, USER_INDEX_FILE, USER_DATA_FILE)
        _, hash_str = user_data.split("|")
        is_authenticated = verify_password(password, hash_str)
        if is_authenticated:
            messagebox.showinfo(message="You are authorized!")
            state["user"] = username
            movie_window = create_or_replace_window(
                app, active_window, 'Movies')
            active_window = movie_window
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


def login_signup():
    global app
    global active_window
    login_window = create_or_replace_window(
        app, active_window, 'Login / Signup')
    active_window = login_window
    login_header = header(login_window, "Login or Signup as a Critic")
    login_header.pack()
    login_frame = centered_frame(login_window)
    username_frame = frame(login_window)
    username_label = form_label(username_frame, "Username")
    username_label.grid()
    username_field = input_text(username_frame)
    username_field.grid(row=0, column=1)
    username_frame.pack()
    password_frame = frame(login_window)
    password_label = form_label(password_frame, "Password")
    password_label.grid()
    password_field = input_text(password_frame)
    password_field.grid(row=0, column=1)
    password_frame.pack()
    login_button = button(
        login_window, "Login / Signup", lambda: login_user(
            username_field, password_field)
    )
    login_button.pack()
    login_frame.pack()


def start():
    global app
    global active_window
    start_window = create_or_replace_window(app, active_window, 'Box Office')
    active_window = start_window
    start_window.title("Box Office")
    start_window.geometry(window_geometry)
    start_window.configure(background=bg_color)
    title = header(start_window, "Box Office")
    title.pack()

    center_frame = centered_frame(start_window)
    center_frame.pack()
    login_button = button(center_frame, "Continue as critic", login_signup)
    login_button.pack()
    view_button = button(center_frame, "View as user", None)
    view_button.pack()


start()

app.mainloop()
