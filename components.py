from tkinter import *
from theme import *


def header(root, title):
    x = Label(
        root,
        pady=4,
        text=title,
        fg=font_color,
        bg=bg_color,
        font=("bold", 32),
        justify="center",
    )
    return x


def new_window(root, title):
    x = Toplevel(root)
    x.geometry(window_geometry)
    x.resizable(False, False)
    x.title(title)
    x.configure(bg=bg_color)
    return x


def button(root, title, command):
    x = Button(root, text=title, highlightbackground=bg_color, command=command)
    return x


def frame(root):
    x = Frame(root, padx=4, pady=4, bg=bg_color)
    return x


def centered_frame(root):
    x = frame(root)
    x.place(relx=0.5, rely=0.5)
    return x


def form_label(root, title):
    x = Label(root, text=title, padx=2, bg=bg_color, fg=font_color)
    return x


def input_text(root):
    x = Entry(root, width=30)
    return x