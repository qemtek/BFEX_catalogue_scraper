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


def get_venue_groups():
    """Get the groups for each horse racing venue (used to avoid hitting the
    limit on market subscriptions in the betfair exchange API)"""
    groups = {
        "A": [
            "Southwell",
            "Newcastle",
            "Bath",
            "Beverley",
            "Newmarket",
            "Catterick",
            "Sandown",
            "Chepstow",
        ],
        "B": [
            "Windsor",
            "Nottingham",
            "Leicester",
            "Goodwood",
            "York",
            "Ayr",
            "Thirsk",
            "Chester",
            "Ffos-Las",
        ],
        "C": [
            "Kempton",
            "Doncaster",
            "Brighton",
            "Yarmouth",
            "Ascot",
            "Newbury",
            "Musselburgh",
            "Pontefract",
            "Carlisle",
            "Warwick",
        ],
        "D": [
            "Chelmsford",
            "Haydock",
            "Hamilton",
            "Redcar",
            "Ripon",
            "Salisbury",
            "Epsom",
            "Wetherby",
            "Lingfield",
        ],
    }
    return groups
