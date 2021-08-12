from tkinter import *
from theme import window_geometry


def label(root, text: str, justify="left"):
    x = Label(
        root,
        text=text,
        padx=1,
        pady=1,
        justify=justify,
    )
    return x


def header(root, title: str):
    x = Label(
        root,
        pady=4,
        text=title,
        font=("bold", 32),
        justify="center",
    )
    return x


def new_window(root, title: str):
    x = Toplevel(root)
    x.geometry(window_geometry)
    x.resizable(False, False)
    x.title(title)
    return x


def button(root, title: str, command, fg="black"):
    x = Button(root, text=title, fg=fg, command=command)
    return x


def frame(root):
    x = Frame(root, padx=4, pady=4)
    return x


def padded_frame(root):
    x = frame(root)
    x.configure(pady=4)
    return x


def form_label(root, title: str):
    x = Label(root, text=title, padx=2, width=14, justify=RIGHT)
    return x


def input_text(root, text: StringVar):
    x = Entry(root, width=30, textvariable=text)
    return x


def divider(root, justify="left"):
    return label(root, "".center(100, "-"), justify=justify)
