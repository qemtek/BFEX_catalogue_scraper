import errno
import os.path


def mkdir_p(path):
    """Open a directory, create a new directory if it dosent exist.
        Taken from https://stackoverflow.com/a/600612/119527
        :param path: The directory where the folder should be created"""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def safe_open(path, access_type):
    """Open a connection to a path without encountering an error if the path
        dosent exist.
        :param path: The path to the file you want to open
        :param access_type: How you want to access the file ('r', 'w', 'rb', 'wb')"""
    mkdir_p(os.path.dirname(path))
    return open(path, access_type)
