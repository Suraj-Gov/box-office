from tkinter import *
from tkinter import messagebox
from theme import *
from components import *
import hashlib
import os
import binascii

app = Tk()
app.resizable(False, False)

state = {
    'user': {
        'name': None
    }
}


def create_user(username, password, login_data_file):
    password_hash = get_password_hash(password)
    login_data = "\n" + username + "|" + password_hash
    login_data_file.write(login_data)
    messagebox.showinfo(message='User successfully created')


def ask_if_user_wants_to_sign_up(username, password, login_data_file):
    does_want_signup = messagebox.askyesno(
        message=f'There are no users with username - {username}.\n Do you want to signup?')
    if does_want_signup:
        create_user(username, password, login_data_file)
        return True
    else:
        return False


def get_password_hash(password):
    salt = hashlib.sha256(os.urandom(64)).hexdigest().encode('ascii')
    hash_str = hashlib.pbkdf2_hmac(
        'sha512', password.encode('utf-8'), salt, 32)
    hash_str = binascii.hexlify(hash_str)
    return (hash_str + salt).decode('ascii')


def login_user(username_field, password_field):
    username = username_field.get()
    password = password_field.get()
    with open("login_data.txt", 'a+') as login_data_file:
        login_data = login_data_file.read()
        # if file is empty
        if login_data == "":
            user_signed_up = ask_if_user_wants_to_sign_up(
                username, password, login_data_file)
            if user_signed_up:
                state['user'] = username
                return
            else:
                return
        # split them into username|password
        user_credentials = login_data.split("\n")

        if user_credentials[0] == "":
            user_credentials = user_credentials[1:]

        print(len(user_credentials), 'number of users')

        for user in user_credentials:
            user, existing_pass_hash = user.split("|")
            if user == username:
                messagebox.showinfo(message='user exists!')
                # TODO password check
                break
            else:
                ask_if_user_wants_to_sign_up(
                    username, password, login_data_file)


def login_signup():
    global app
    login_signup_window = new_window(app, 'Login or Signup')
    login_header = header(login_signup_window, 'Login')
    login_header.pack()
    login_frame = centered_frame(login_signup_window)
    username_frame = frame(login_signup_window)
    username_label = form_label(username_frame, 'Username')
    username_label.grid()
    username_field = input_text(username_frame)
    username_field.grid(row=0, column=1)
    username_frame.pack()
    password_frame = frame(login_signup_window)
    password_label = form_label(password_frame, 'Password')
    password_label.grid()
    password_field = input_text(password_frame)
    password_field.grid(row=0, column=1)
    password_frame.pack()
    login_button = button(login_signup_window, 'Login',
                          lambda: login_user(username_field, password_field))
    login_button.pack()
    login_frame.pack()


def start():
    global app
    app.title('Box Office')
    app.geometry(window_geometry)
    app.configure(background=bg_color)
    title = header(app, 'Box Office')
    title.pack()

    center_frame = centered_frame(app)
    center_frame.pack()
    login_button = button(center_frame, 'Continue as critic', login_signup)
    login_button.pack()
    view_button = button(center_frame, 'View as user', None)
    view_button.pack()


start()

app.mainloop()
