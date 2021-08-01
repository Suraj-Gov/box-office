import tkinter
from filenames import USER_INDEX_FILE
import os
import binascii
import hashlib
from theme import *


# https://www.py4u.net/discuss/172694
def create_or_replace_window(root, title, current_window=None):
    """Destroy current window if current_window is provided, create new window"""
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


def get_offset(filename, search_str):
    """requires a index key to search,
    returns offset in Int
    if no index found, returns -1"""
    # get offset from the key provided (used for index files)
    search_arr = []
    with open(filename, "a+") as file_data:
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


def get_record(key, index_filename, record_filename, provided_offset=-1):
    """requires index key, optional provided_offset
    returns record/data string
    returns False if no record found"""
    offset = provided_offset if provided_offset != -1 else get_offset(
        index_filename, key)
    if offset == -1:
        return False
    with open(record_filename, 'a+') as record_file:
        record_file.seek(offset)
        record_str = record_file.readline()
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
        record_lines = list(
            map(
                lambda x: record_lines.append(x),
                record_file_data.read().split("\n")
            )
        )
    return record_lines if len(record_lines) > 1 else False if record_lines[0] == "" else record_lines


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


def check_key_exist(key, index_file):
    """checks key existance
    returns True if exists
    returns False if not"""
    offset = get_offset(index_file, key)
    if offset != -1:
        return True
    return False


def create_record(record_filename, index_filename, key, data):
    """creates a record
    needs a key as primary key
    data is just a string
    returns None if key already exists
    returns True if record created successfully"""
    does_key_exist = check_key_exist(key, index_filename)
    if does_key_exist:
        return None
    with open(record_filename, "a+") as record_data:
        # write the data at the end of file
        record_data.seek(0, os.SEEK_END)
        start_pos = record_data.tell()
        record_data.write(data + "\n")
        with open(index_filename, 'a+') as index_data:
            index_data.seek(0)
            # open index_file and read to array
            idx_arr = read_index_file(USER_INDEX_FILE)
            # if no indexes exist
            # if len(idx_arr) == 0:
            #     index_data.write(f"{key}|{start_pos}\n")
            #     return True
            # # if only one index exist
            # if len(idx_arr) == 1:
            #     if idx_arr[0][0] < key:
            #         index_data.write(f"{key}|{start_pos}\n")
            #     else:
            #         index_data.seek(0, os.SEEK_SET)
            #         index_data.write(f"{key}|{start_pos}\n")
            #     return True
            # else:
            if True:
                # if multiple indexes exist do a binary_search
                l = 0
                idx_arr_len = len(idx_arr)
                r = idx_arr_len - 1
                next_idx = None
                while l <= r:
                    mid = (l + r) // 2
                    idx, _ = idx_arr[mid]
                    if idx < key:
                        l = mid + 1
                        # idx@mid < key < idx@mid+1 (between those two), insert between them
                        if key < idx_arr[l][0]:
                            next_idx = idx_arr[l][0]
                            idx_arr.insert(l, key)
                            break
                    elif idx > key:
                        r = mid - 1
                        # idx@mid-1 < key < idx#mid (between those two), insert between them
                        if key > idx_arr[r][0]:
                            next_idx = idx_arr[mid][0]
                            idx_arr.insert(mid, key)
                            break
                # finish inserting, write to the file
                # write just before the next index
                pos_before_next_idx = get_offset(index_filename, next_idx)
                if(pos_before_next_idx == -1):
                    pos_before_next_idx = 0
                index_data.seek(pos_before_next_idx)
                index_data.write(f"{key}|{start_pos}\n")
                return True


def get_password_hash(password):
    """generate hash for a plaintext password"""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(provided_password, stored_password):
    """compare and check if the given plaintext password is equal to the hashed password stored"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    is_authenticated = pwdhash == stored_password
    if is_authenticated:
        print("user authenticated")
        return True
    return False
