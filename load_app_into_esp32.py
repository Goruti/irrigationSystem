import os
import posixpath
import subprocess

import ampy.files as files
import ampy.pyboard as pyboard

PORT = '/dev/tty.usbserial-0001'
BAUD = 115200
DELAY = 1.5
APP_ROOT_DIR = "src/"
_board = None


def build_bytecode(root_dir):
    # Check if path is a folder and do recursive copy of everything inside it.
    # Otherwise it's a file and should simply be copied over.
    remote="/"
    if os.path.isdir(root_dir):
        # Directory copy, create the directory and walk all children to copy
        # over the files.
        for parent, child_dirs, child_files in os.walk(root_dir, followlinks=True):
            # Create board filesystem absolute path to parent directory.
            remote_parent = posixpath.normpath(
                posixpath.join(remote, os.path.relpath(parent, root_dir))
            )
            for filename in list(filter(keep_py_files, child_files)):
                full_name = os.path.join(parent, filename)
                remote_filename = posixpath.join(remote_parent, filename)

                print("bytecode file '{}' as '{}'".format(full_name, remote_filename))

                subprocess.call(["./mpy-cross", "-s", remote_filename, full_name])


def keep_py_files(filename):
    if os.path.splitext(filename)[1] in [".py"] and filename not in ['boot.py', 'main.py']:
        return True
    return False

def filter_files_type(filename):
    if filename in ["boot.py", "main.py"] or os.path.splitext(filename)[1] in [".mpy", ".gz"]:
        return True
    return False


def load_files(root_dir):
    global _board
    _board = pyboard.Pyboard(PORT, baudrate=BAUD, rawdelay=DELAY)
    dir_files = ["{}{}".format(root_dir, x) for x in os.listdir(root_dir)]
    list(map(put, dir_files))


def put(local, remote=None):
    global _board
    board_files = files.Files(_board)
    # Use the local filename if no remote filename is provided.
    print("working with file/directory: {}".format(local))
    if remote is None:
        remote = os.path.basename(os.path.abspath(local))
    # Check if path is a folder and do recursive copy of everything inside it.
    # Otherwise it's a file and should simply be copied over.
    if os.path.isdir(local):
        # Directory copy, create the directory and walk all children to copy over the files.

        for parent, child_dirs, child_files in os.walk(local, followlinks=True):
            # Create board filesystem absolute path to parent directory.
            remote_parent = posixpath.normpath(
                posixpath.join(remote, os.path.relpath(parent, local))
            )

            # Create remote parent directory.
            board_files.mkdir(remote_parent, exists_okay=True)

            # Loop through all the FILTERED files and put them on the board too.
            for filename in list(filter(filter_files_type, child_files)):
                with open(os.path.join(parent, filename), "rb") as infile:
                    remote_filename = posixpath.join(remote_parent, filename)
                    print("Loading file: '{}' to '{}'".format(os.path.join(parent, filename), remote_filename))
                    board_files.put(remote_filename, infile.read())
    else:
        # File copy, open the file and copy its contents to the board.
        # Put the file on the board.
        print("Loading file: {}".format(local))
        with open(local, "rb") as infile:
            print("Loading file '{}' to '{}'".format(local, remote))
            board_files.put(remote, infile.read())


def loaded_files(directory="/", long_format=True, recursive=True):
    global _board
    _board = pyboard.Pyboard(PORT, baudrate=BAUD, rawdelay=DELAY)
    board_files = files.Files(_board)
    for files_names in board_files.ls(directory, long_format=long_format, recursive=recursive):
        print(files_names)


def main():
    print("####### GENERATING BYTECODES ##########")
    build_bytecode(APP_ROOT_DIR)
    print("####### LOADING FILES... ##########")
    load_files(APP_ROOT_DIR)
    print("#######LOADED FILES ##########")
    loaded_files()


if __name__ == "__main__":
    try:
        main()
    finally:
        # Try to ensure the board serial connection is always gracefully closed.
        if _board:
            try:
                _board.close()
            except:
                pass
