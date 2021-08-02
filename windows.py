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


def render_view_movies_window(app, active_window):

    movies_list = None
    # hoisting up the movies_list Listbox

    def add_update_movie(app):
        render_add_update_movies_window(app)

    movie_data = []

    def load_movies(movies_list):
        movies_list.delete(0, movies_list.size() - 1)
        movie_data = get_all_records(MOVIE_DATA_FILE)
        for movie_record_str in movie_data:
            movie_title = movie_record_str.split("|")[0]
            movies_list.insert(END, movie_title)

    view_movies_window = create_or_replace_window(app, 'Movies', active_window)
    active_window = view_movies_window
    button_frames = frame(view_movies_window)
    button_frames.pack()
    button(
        button_frames, 'Add / Update Movie', lambda: add_update_movie(app)).grid()
    button(button_frames, 'Refresh movies', lambda: load_movies(
        movies_list)).grid(row=0, column=1)

    movie_indexes = read_index_file(MOVIE_INDEX_FILE)
    if len(movie_indexes) == 0:
        no_movies_stored_label = label(
            view_movies_window, text='No movies stored', justify=CENTER)
        no_movies_stored_label.pack()
    else:
        scroll = Scrollbar(view_movies_window)
        scroll.pack(side=RIGHT, fill=Y)
        movies_list = Listbox(
            view_movies_window, bg=bg_color, fg=font_color, yscrollcommand=scroll.set, height=30, font=('bold', 28), selectbackground=lighter_bg_color)
        load_movies(movies_list)
        scroll.config(command=movies_list.yview)
        movies_list.pack(fill=X)

        def select_movie(_):
            idx = movies_list.curselection()[0]
            print(movie_data[idx])

        movies_list.bind("<<ListboxSelect>>", select_movie)

    return view_movies_window


def render_add_update_movies_window(app):

    def run(movie_title: str):
        movie_status = add_update_movie(movie_title)
        if movie_status is False:
            return
        else:
            if movie_status == True:
                render_movie_details_window(app, None, movie_title)
            else:
                render_movie_details_window(app, movie_status)

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
    add_update_button = button(title_frame, 'Add / Update Movie',
                               lambda: run(title_str_var.get()))
    add_update_button.configure(pady=6)
    add_update_button.pack()
    return add_update_movie_window


def render_movie_details_window(app, movie_record=None, title=''):
    """provide app, and movie_record str (optional)"""
    movie_record = None if not movie_record else movie_record.split("|")
    movie_title = None if not movie_record else movie_record[0]
    window_title = "Add Movie" if not movie_title else f"Update Movie - {movie_title}"
    movie_details_window = create_or_replace_window(
        app, window_title
    )
    main_frame = frame(movie_details_window)
    main_frame.place(relx=0.5, rely=0.5, anchor='center')
    title_str_var = StringVar()
    title_str_var.set("" if not movie_record else movie_title)
    if title != '':
        title_str_var.set(title)
    director_str_var = StringVar()
    director_str_var.set("" if not movie_record else movie_record[1])
    cast_str_var = StringVar()
    cast_str_var.set("" if not movie_record else movie_record[2])
    about_str_var = StringVar()
    about_str_var.set("" if not movie_record else movie_record[3])
    if movie_title:
        header(movie_details_window, movie_title).pack()
    else:
        title_frame = padded_frame(main_frame)
        form_label(title_frame, 'Movie Title').grid(row=0, column=0)
        input_text(title_frame, title_str_var).grid(row=0, column=1)
        title_frame.pack()
    row = 1 if not movie_title else 0
    director_frame = padded_frame(main_frame)
    form_label(director_frame, 'Director').grid(row=row, column=0)
    input_text(director_frame, director_str_var).grid(row=row, column=1)
    director_frame.pack()
    row += 1
    cast_frame = padded_frame(main_frame)
    form_label(cast_frame, 'Cast').grid(row=row, column=0)
    input_text(cast_frame, cast_str_var).grid(row=row, column=1)
    cast_frame.pack()
    row += 1
    about_frame = padded_frame(main_frame)
    form_label(about_frame, 'About').grid(row=row, column=0)
    input_text(about_frame, about_str_var).grid(row=row, column=1)
    about_frame.pack()
    button_text = "Add Movie" if not movie_record else "Update Movie"
    cta = button(main_frame, button_text, lambda: add_update_movie_record(
        title_str_var.get(), director_str_var.get(), cast_str_var.get(), about_str_var.get(), "ADD" if not movie_record else "UPDATE"))
    cta.configure(pady=2)
    cta.pack()
    return movie_details_window
