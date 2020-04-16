import errno
import os.path


# Taken from https://stackoverflow.com/a/600612/119527
def mkdir_p(path):
    """Open a directory, create a new directory if it dosent exist"""

    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def safe_open(path, access_type):
    """Open a connection to a path without encountering an error if the path
    dosent exist"""

    mkdir_p(os.path.dirname(path))
    return open(path, access_type)
