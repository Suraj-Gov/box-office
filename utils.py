from io import SEEK_END, SEEK_SET
import tkinter
from filenames import MOVIE_DATA_FILE, USER_INDEX_FILE
import os
import binascii
import hashlib
from theme import *
from tempfile import mkstemp
from shutil import move, copymode

RECORD_LENGTH = 511
# line-break at end


def write_between_file(filename, before_str, data, write_type="ADD"):
    """write between file
    should provide a line-break
    if writing to empty file, provide empty str to before_str"""
    # https://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python
    temp_fd, abs_path = mkstemp()
    old_file = open(filename, "a+")
    old_file.seek(0, SEEK_SET)
    old_file_abs_path = os.path.abspath(filename)
    with os.fdopen(temp_fd, "w") as new_file:
        new_data = ""
        if before_str == "":
            # this is used when the file is empty
            new_file.write(data)
        else:
            # this is used when the file has some data in it
            for line in old_file:
                if line != before_str:
                    new_data += line
                else:
                    if write_type == "ADD":
                        new_data += data + line
                    else:
                        new_data += data
        old_file.close()
        new_file.write(new_data)
    copymode(old_file_abs_path, abs_path)
    os.remove(old_file_abs_path)
    move(abs_path, old_file_abs_path)


def create_or_replace_window(root, title, current_window=None):
    """Destroy current window if current_window is provided, create new window"""
    # https://www.py4u.net/discuss/172694
    if current_window is not None:
        current_window.destroy()
    new_window = tkinter.Toplevel(root)
    new_window.title(title)
    new_window.geometry(window_geometry)
    new_window.resizable(False, False)
    new_window.title(title)
    new_window.configure(bg=bg_color)

    # if the user kills the window via the window manager,
    # exit the application.
    if current_window != None:
        new_window.wm_protocol("WM_DELETE_WINDOW", root.destroy)

    return new_window


def get_offset(index_filename, search_str):
    """requires a index key to search,
    returns offset in Int
    if no index found, returns -1"""
    # get offset from the key provided (used for index files)
    search_arr = []
    with open(index_filename, "a+") as file_data:
        file_data.seek(0)
        for line_str in file_data:
            line = line_str.strip()
            if line == "":
                continue
            line_id, record_offset = line.split("|")
            search_arr.append((line_id, record_offset))
    l = 0
    r = len(search_arr) - 1
    while l <= r:
        mid = (l + r) // 2
        idx, offset = search_arr[mid]
        if idx == search_str:
            return int(offset)
        elif idx < search_str:
            l = mid + 1
        else:
            r = mid - 1
    return -1


def get_record(key, index_filename, record_filename, provided_offset=-1, unpadded=True):
    """requires index key, optional provided_offset(int)
    returns record/data string
    returns False if no record found"""
    offset = (
        provided_offset if provided_offset != -1 else get_offset(index_filename, key)
    )
    if offset == -1:
        return False
    with open(record_filename, "a+") as record_file:
        record_file.seek(offset)
        record_str = record_file.readline()
        if unpadded:
            record_str = record_str.strip()
        return record_str


def get_all_records(record_filename):
    """
    requires DATA_FILE
    returns record_line[]
    returns False if no records are in file yet
    """
    record_lines = []
    with open(record_filename, "a+") as record_file_data:
        record_file_data.seek(0, os.SEEK_SET)
        record_lines = record_file_data.read().split("\n")
        record_lines = list(map(lambda x: x.strip(), record_lines))
        record_lines = list(filter(lambda x: x != "", record_lines))
        return (
            record_lines
            if len(record_lines) > 1
            else False
            if record_lines[0] == ""
            else record_lines
        )


def read_index_file(filename):
    """reads a index file,
    returns (idx, offset)[]
    check for empty array if no keys are found"""
    arr = []
    with open(filename, "a+") as file_data:
        file_data.seek(0)
        for line_str in file_data:
            line = line_str.strip()
            if line == "":
                continue
            line_id, record_offset = line.split("|")
            arr.append((line_id, record_offset))
    return arr


def check_key_exist(key, index_filename):
    """checks key existance
    returns True if exists
    returns False if not"""
    offset = get_offset(index_filename, key)
    if offset != -1:
        return True
    return False


def create_record(record_filename: str, index_filename: str, key: str, data: str):
    """creates a record
    needs a key as primary key
    data is just a non padded string
    returns True if record created successfully"""
    does_key_exist = check_key_exist(key, index_filename)
    if does_key_exist:
        return None
    data = data.ljust(RECORD_LENGTH, " ")
    with open(record_filename, "a+") as record_data:
        # write the data at the end of file
        record_data.seek(0, os.SEEK_END)
        start_pos = record_data.tell()
        record_data.write(data + "\n")
        with open(index_filename, "a+") as index_data:
            index_data.seek(0)
            # open index_file and read to array
            idx_arr = read_index_file(index_filename)
            l = 0
            r = len(idx_arr) - 1
            next_idx = None
            while l <= r:
                mid = (l + r) // 2
                idx, _ = idx_arr[mid]
                if idx < key:
                    l = mid + 1
                    # idx@mid < key < idx@mid+1 (between those two), insert between them
                    try:
                        if key < idx_arr[l][0]:
                            next_idx = "|".join(idx_arr[l])
                            idx_arr.insert(l, key)
                            break
                    except IndexError:
                        idx_arr.append(key)
                        next_idx = idx_arr[-1]
                elif idx > key:
                    r = mid - 1
                    # idx@mid-1 < key < idx#mid (between those two), insert between them
                    try:
                        if key > idx_arr[r][0]:
                            next_idx = "|".join(idx_arr[r])
                            idx_arr.insert(mid, key)
                            break
                    except:
                        idx_arr.insert(0, key)
                        next_idx = idx_arr[0][0]
            # finish inserting, write to the file
            # write just before the next index
            idx_str = f"{key}|{start_pos}\n"
            if next_idx == key:
                # this means the key has to be written at the end
                with open(index_filename, "a+") as idx_file:
                    idx_file.write(idx_str)
            else:
                if next_idx is None:
                    # this means the index_file is empty and this is the first idx to be added
                    write_between_file(index_filename, "", idx_str)
                # this means the key has to written at the start of the file
                else:
                    write_between_file(index_filename, next_idx + "\n", idx_str)
        return True


def update_record(record_filename: str, index_filename: str, key: str, record_str: str):
    """provide the key and record_str, should provide padded str for data_files"""
    does_key_exist = check_key_exist(key, index_filename)
    if does_key_exist:
        replace_str = get_record(key, index_filename, record_filename, unpadded=False)
        write_between_file(
            record_filename, replace_str, record_str + "\n", write_type="REPLACE"
        )
        return True
    else:
        return None


def get_password_hash(password):
    """generate hash for a plaintext password"""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode("ascii")


def verify_password(provided_password, stored_password):
    """compare and check if the given plaintext password is equal to the hashed password stored"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
    )
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    is_authenticated = pwdhash == stored_password
    if is_authenticated:
        print("user authenticated")
        return True
    return False
