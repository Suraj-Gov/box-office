from controller import *
from theme import *
from components import *
from filenames import *
from utils import *


def render_start_window(app, active_window, cfn_critic, cfn_user):
    """Generate start window, provide a click fn to buttons"""
    start_window = create_or_replace_window(app, 'Box Office', active_window)
    start_window.title("Box Office")
    start_window.geometry(window_geometry)
    start_window.configure(background=bg_color)
    title = header(start_window, "Box Office")
    title.pack()

    center_frame = frame(start_window)
    center_frame.place(relx=0.5, rely=0.5, anchor='center')
    login_button = button(center_frame, "Continue as critic", cfn_critic)
    login_button.pack()
    view_button = button(center_frame, "View as user", cfn_user)
    view_button.pack()
    return start_window


def render_login_signup_window(app, active_window, username_str_var, password_str_var, cfn_login):
    """Generate login_signup window, provide a cfn (username_field, password_field)"""

    login_window = create_or_replace_window(
        app,  'Login / Signup', active_window)
    active_window = login_window
    login_header = header(login_window, "Login or Signup as a Critic")
    login_header.pack()
    login_frame = frame(login_window)
    username_frame = frame(login_frame)
    username_label = form_label(username_frame, "Username")
    username_label.grid()
    username_field = input_text(username_frame, username_str_var)
    username_field.grid(row=0, column=1)
    username_frame.pack()
    password_frame = frame(login_frame)
    password_label = form_label(password_frame, "Password")
    password_label.grid()
    password_field = input_text(password_frame, password_str_var)
    password_field.grid(row=0, column=1)
    password_frame.pack()
    login_button = button(
        login_frame, "Login / Signup", cfn_login
    )
    login_button.pack()
    login_frame.place(relx=0.5, rely=0.5, anchor='center')
    return login_window


def render_view_movies_window(app, active_window, add_update_movie):
    view_movies_window = create_or_replace_window(app, 'Movies', active_window)
    active_window = view_movies_window
    button_frames = frame(view_movies_window)
    button_frames.pack()
    add_update_movie_button = button(
        button_frames, 'Add / Update Movie', add_update_movie)
    add_update_movie_button.pack()
    movie_indexes = read_index_file(MOVIE_INDEX_FILE)
    if len(movie_indexes) == 0:
        no_movies_stored_label = label(
            view_movies_window, text='No movies stored', justify='center')
        no_movies_stored_label.pack()
    else:
        movies_frame = frame(view_movies_window)
        movies_frame.pack()
        movie_data = get_all_records(MOVIE_DATA_FILE)
        for movie in movie_data:
            label(movies_frame, movie).pack()
    return view_movies_window


def render_add_update_movies_window(app):
    add_update_movie_window = create_or_replace_window(
        app, 'Add / Update Movie')
    title_str_var = StringVar(app)
    title_frame = frame(add_update_movie_window)
    title_frame.pack()
    title_label = label(title_frame, 'Enter the movie title',
                        justify='center')
    title_label.configure(pady=5)
    title_label.pack()
    input_text(title_frame, text=title_str_var).pack()
