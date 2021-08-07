from controller import *
from theme import *
from components import *
from filenames import *
from utils import *
from typing import List
import state


def render_start_window(app: Tk, active_window: Toplevel, cfn_critic, cfn_user):
    """Generate start window, provide a click fn to buttons"""
    start_window = create_or_replace_window(app, "Box Office", active_window)
    start_window.title("Box Office")
    start_window.geometry(window_geometry)
    start_window.configure(background=bg_color)
    title = header(start_window, "Box Office")
    title.pack()

    center_frame = frame(start_window)
    center_frame.place(relx=0.5, rely=0.5, anchor="center")
    login_button = button(center_frame, "Continue as critic", cfn_critic)
    login_button.pack()
    view_button = button(center_frame, "View as user", cfn_user)
    view_button.pack()
    return start_window


def render_login_signup_window(
    app: Tk,
    active_window: Toplevel,
    username_str_var: StringVar,
    password_str_var: StringVar,
    cfn_login,
):
    """Generate login_signup window, provide a cfn (username_field, password_field)"""

    login_window = create_or_replace_window(app, "Login / Signup", active_window)
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
    login_button = button(login_frame, "Login / Signup", cfn_login)
    login_button.pack()
    login_frame.place(relx=0.5, rely=0.5, anchor="center")
    return login_window


def render_view_movies_window(app: Tk, active_window: Toplevel):

    movies_list = None
    search_str_var = StringVar()
    # hoisting up the movies_list Listbox and search_str_var

    def add_update_movie(app: Tk):
        render_add_update_movies_window(app)

    def search(e: Event):
        search_val = search_str_var.get() + e.char
        print(search_val)
        search_movies(movies_list, movie_data, search_val)

    movie_data = []
    window = create_or_replace_window(app, "Movies", active_window)
    active_window = window
    label(window, "Search movies", justify="center").pack(pady=3)
    search_text = input_text(window, search_str_var)
    search_text.bind("<Key>", search)
    search_text.pack()
    divider(window, justify="center").pack()
    if state.user:
        label(active_window, f"Hey, {state.user}", justify="center").pack()
    button_frames = frame(window)
    if state.user:
        button_frames.pack()
    button(button_frames, "Add / Update Movie", lambda: add_update_movie(app)).grid(
        row=1, column=0
    )
    button(button_frames, "⟳", lambda: load_movies(movies_list, movie_data)).grid(
        row=1, column=1
    )

    movie_indexes = read_index_file(MOVIE_INDEX_FILE)
    if len(movie_indexes) == 0:
        no_movies_stored_label = label(window, text="No movies stored", justify=CENTER)
        no_movies_stored_label.pack()
    else:
        scroll = Scrollbar(window)
        scroll.pack(side=RIGHT, fill=Y)
        movies_list = Listbox(
            window,
            bg=bg_color,
            fg=font_color,
            yscrollcommand=scroll.set,
            height=30,
            font=("bold", 28),
            selectbackground=lighter_bg_color,
        )
        load_movies(movies_list, movie_data)
        scroll.config(command=movies_list.yview)
        movies_list.pack(fill=X)

        def select_movie(_):
            idx = movies_list.curselection()[0]
            movie_title, offset = movie_data[idx].split("|")
            data = get_record(
                movie_title,
                MOVIE_INDEX_FILE,
                MOVIE_DATA_FILE,
                int(offset),
                unpadded=True,
            )
            if state.user:
                render_movie_details_edit_window(app, movie_record=data)
            else:
                render_movie_details_view_window(app, data)

        movies_list.bind("<<ListboxSelect>>", select_movie)

    return window


def render_add_update_movies_window(app: Tk):
    def add_update_movie_fn(movie_title: str):
        movie_status = add_update_movie(movie_title)
        if movie_status is False:
            return
        else:
            if movie_status == True:
                render_movie_details_edit_window(app, None, movie_title)
            else:
                render_movie_details_edit_window(app, movie_status)

    add_update_movie_window = create_or_replace_window(app, "Add / Update Movie")
    title_str_var = StringVar(app)
    title_frame = frame(add_update_movie_window)
    title_frame.pack()
    title_label = label(title_frame, "Enter the movie title", justify="center")
    title_label.configure(pady=5)
    title_label.pack()
    input_text(title_frame, text=title_str_var).pack()
    button(
        title_frame,
        "Add / Update Movie",
        lambda: add_update_movie_fn(title_str_var.get()),
    ).pack()
    return add_update_movie_window


def render_movie_details_view_window(app: Tk, movie_record: str):
    """provide app, movie_record(str)(unpadded), should show only a saved movie"""
    title, director, cast, about, rating_str = movie_record.split("|")
    window = create_or_replace_window(app, f"Movie details - {title}")
    header(window, title).pack()
    rating = int(rating_str)
    label(window, "★" * rating).pack()
    label(window, f"Directed by: {director}").pack()
    divider(window, justify="center").pack()
    label(window, "Cast:").pack()
    cast_individuals = list(map(lambda x: x.strip(), cast.split(",")))
    for individual in cast_individuals:
        label(window, individual).pack()
    divider(window, justify="center").pack()
    label(window, "About the movie:").pack()
    label(window, about).pack()
    return window


def render_movie_details_edit_window(app: Tk, movie_record=None, title=""):
    """provide app, and movie_record str (optional)"""

    def add_update_movie_record_fn(
        title: str,
        director: str,
        cast: str,
        about: str,
        rating: str,
        opt: str,
        window: Toplevel,
    ):
        successfully_added = add_update_movie_record(
            title, director, cast, about, rating, opt
        )
        if successfully_added:
            msg = "Sucessfully "
            msg += "added" if opt == "ADD" else "updated"
            msg += f" movie - {title}"
            messagebox.showinfo(message=msg)
            window.destroy()
        else:
            messagebox.showerror(message=f"Couldn't add movie - {title}")

    def delete_movie_record(title: str, window: Toplevel):
        wanna_delete_movie = messagebox.askokcancel(
            message=f"Are you sure you want to delete movie - {title}"
        )
        if not wanna_delete_movie:
            return
        successfully_deleted = delete_record(MOVIE_DATA_FILE, MOVIE_INDEX_FILE, title)
        if successfully_deleted:
            messagebox.showinfo(message="Successfully deleted movie")
            window.destroy()
        else:
            messagebox.showerror(message="Couldn't delete movie")

    movie_record = None if not movie_record else movie_record.split("|")
    movie_title = None if not movie_record else movie_record[0]
    window_title = "Add Movie" if not movie_title else f"Update Movie - {movie_title}"
    window = create_or_replace_window(app, window_title)
    main_frame = frame(window)
    main_frame.place(relx=0.5, rely=0.5, anchor="center")
    title_str_var = StringVar()
    title_str_var.set("" if not movie_record else movie_title)
    if title != "":
        title_str_var.set(title)
    director_str_var = StringVar()
    director_str_var.set("" if not movie_record else movie_record[1])
    cast_str_var = StringVar()
    cast_str_var.set("" if not movie_record else movie_record[2])
    about_str_var = StringVar()
    about_str_var.set("" if not movie_record else movie_record[3])
    if movie_title:
        header(window, movie_title).pack()
    else:
        title_frame = padded_frame(main_frame)
        form_label(title_frame, "Movie Title").grid(row=0, column=0)
        input_text(title_frame, title_str_var).grid(row=0, column=1)
        title_frame.pack()
    director_frame = padded_frame(main_frame)
    form_label(director_frame, "Director").grid(row=0, column=0)
    input_text(director_frame, director_str_var).grid(row=0, column=1)
    director_frame.pack()
    cast_frame = padded_frame(main_frame)
    form_label(cast_frame, "Cast").grid(row=0, column=0)
    input_text(cast_frame, cast_str_var).grid(row=0, column=1)
    cast_frame.pack()
    about_frame = padded_frame(main_frame)
    form_label(about_frame, "About").grid(row=0, column=0)
    input_text(about_frame, about_str_var).grid(row=0, column=1)
    about_frame.pack()
    ratings_frame = padded_frame(main_frame)
    form_label(ratings_frame, "Choose a rating ").grid(row=0, column=0)
    rating_str_var = StringVar(
        ratings_frame, value="3" if not movie_record else movie_record[4]
    )
    ratings = {"1 ★": "1", "2 ★": "2", "3 ★": "3", "4 ★": "4", "5 ★": "5"}
    for idx, (k, v) in enumerate(ratings.items()):
        Radiobutton(
            ratings_frame,
            variable=rating_str_var,
            text=k,
            value=v,
            bg=bg_color,
            fg=font_color,
            padx=2,
            foreground="yellow",
        ).grid(column=idx + 1, row=0)
    ratings_frame.pack()
    button_text = "Add Movie" if not movie_record else "Update Movie"
    button_frame = padded_frame(main_frame)
    button(
        button_frame,
        button_text,
        lambda: add_update_movie_record_fn(
            title_str_var.get(),
            director_str_var.get(),
            cast_str_var.get(),
            about_str_var.get(),
            rating_str_var.get(),
            "ADD" if not movie_record else "UPDATE",
            window=window,
        ),
    ).grid(row=0, column=0)
    if button_text == "Update Movie":
        button(
            button_frame,
            "Delete Movie",
            lambda: delete_movie_record(title_str_var.get(), window=window),
        ).grid(row=0, column=1)
    button_frame.pack()
    return window
