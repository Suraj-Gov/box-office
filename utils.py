from io import SEEK_END, SEEK_SET
import tkinter
from typing import List
from filenames import MOVIE_DATA_FILE, USER_INDEX_FILE
import os
import binascii
import hashlib
from theme import *
from tempfile import mkstemp
from shutil import move, copymode

RECORD_LENGTH = 511
# line-break at end


def write_between_file(filename: str, before_str: str, data: str, write_type="ADD"):
    """write between file
    do not provide a line break
    if writing to empty file, provide empty str to before_str"""
    old_file = open(filename, "a+")
    old_file.seek(0, SEEK_SET)
    old_file_content = old_file.readlines()
    new_data = ""
    if data[-1] == "\n":
        data = data[0:-1]
    if before_str == "":
        # this is used when the file is empty or when the data is needed to append at the start
        old_file.seek(0, SEEK_SET)
        old_file_content.insert(0, data)
        old_file.writelines(list(map(lambda x: x + "\n", old_file_content)))
        old_file.close()
    else:
        if data[-1] != "\n":
            data += "\n"
        # this is used when the file has some data in it
        for line in old_file_content:
            if line.strip() != before_str.strip():
                new_data += line
            else:
                if write_type == "ADD":
                    new_data += data + line
                else:
                    new_data += data
        old_file.truncate(0)
        old_file.write(new_data)
    old_file.close()


def create_or_replace_window(root: tkinter.Tk, title: str, current_window=None):
    """Destroy current window if current_window is provided, create new window"""
    # https://www.py4u.net/discuss/172694
    if current_window is not None:
        current_window.destroy()
    new_window = tkinter.Toplevel(root)
    new_window.title(title)
    new_window.geometry(window_geometry)
    new_window.resizable(False, False)
    new_window.title(title)

    # if the user kills the window via the window manager,
    # exit the application.
    if current_window != None:
        new_window.wm_protocol("WM_DELETE_WINDOW", root.destroy)

    return new_window


def get_offset(index_filename: str, search_str: str):
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


def get_record(
    key: str,
    index_filename: str,
    record_filename: str,
    provided_offset=-1,
    unpadded=True,
):
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


def get_all_records(record_filename: str):
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
        return record_lines if len(record_lines) > 0 else []


def read_index_file(filename: str):
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


def check_key_exist(key: str, index_filename: str):
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
            idx_str = f"{key}|{start_pos}"
            if next_idx == key:
                # this means the key has to be written at the end
                with open(index_filename, "a+") as idx_file:
                    idx_file.write(idx_str + "\n")
            else:
                if next_idx is None:
                    # this means the index_file is empty and this is the first idx to be added
                    write_between_file(index_filename, "", idx_str)
                # this means the key has to written at the start of the file
                else:
                    write_between_file(index_filename, next_idx, idx_str)
        return True


def update_record(record_filename: str, index_filename: str, key: str, record_str: str):
    """provide the key and record_str, should provide padded str for data_files"""
    does_key_exist = check_key_exist(key, index_filename)
    if does_key_exist:
        replace_str = get_record(key, index_filename, record_filename, unpadded=False)
        write_between_file(
            record_filename, replace_str, record_str, write_type="REPLACE"
        )
        return True
    else:
        return None


def delete_record(record_filename: str, index_filename: str, key: str):
    """deletes a record and it's index from files"""

    def stringify(x):
        """just converts the int part to str, need to provide a list of two elements"""
        x[1] = str(x[1])
        return "|".join(x) + "\n"

    does_key_exist = check_key_exist(key, index_filename)
    if does_key_exist:
        key_to_delete_offset = get_offset(index_filename, key)
        with open(record_filename, "a+") as record_file_data:
            record_file_data.seek(0)
            old_data = list(map(lambda x: x.strip(), record_file_data.readlines()))
            record_file_data.truncate(0)
            for idx, data in enumerate(old_data):
                record_key = data.split("|")[0]
                if key == record_key:
                    old_data.pop(idx)
                    break
            record_file_data.writelines(
                list(map(lambda x: x.ljust(RECORD_LENGTH) + "\n", old_data))
            )
        with open(index_filename, "a+") as index_file_data:
            index_file_data.seek(0, SEEK_SET)
            # split by "|"
            old_idxs = list(map(lambda x: x.split("|"), index_file_data.readlines()))
            # convert str offsets to int
            old_idxs = list(map(lambda x: [x[0], int(x[1])], old_idxs))
            index_file_data.truncate(0)
            for i, iidx in enumerate(old_idxs):
                idx_offset = iidx[1]
                # if the key equals the key to delete
                if key_to_delete_offset == idx_offset:
                    old_idxs.pop(i)
                    if len(old_idxs) == 0:
                        break
                    # so if the item gets removed, another item shifts to left, so we are checking if that has a higher offset
                if old_idxs[i][1] >= key_to_delete_offset:
                    old_idxs[i][1] -= RECORD_LENGTH + 1
                # else if the key is greater than the delete_offset
                # (because a record is deleted, then we need to reduce the offset by RECORD_LENGTH)
                elif idx_offset >= key_to_delete_offset:
                    iidx[1] -= RECORD_LENGTH + 1
            # converting back to index format and writing to index_file
            index_file_data.writelines(list(map(lambda x: stringify(x), old_idxs)))
            return True
    else:
        return False


def get_password_hash(password: str):
    """generate hash for a plaintext password"""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode("ascii")


def verify_password(provided_password: str, stored_password: str):
    """compare and check if the given plaintext password is equal to the hashed password stored"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", provided_password.encode("utf-8"), salt.encode("ascii"), 100000
    )
    pwdhash = binascii.hexlify(pwdhash).decode("ascii")
    is_authenticated = pwdhash == stored_password
    if is_authenticated:
        return True
    return False
