import logging
import os
import subprocess

from configuration import football
from configuration import logging_level
from configuration import project_dir
from configuration import racing

logging.basicConfig(level=logging_level)


if racing:
    subprocess.Popen(
        "python3 {}.py".format(
            os.path.join(project_dir, "src", "market_streaming_racing")
        ),
        shell=True,
    )
if football:
    subprocess.Popen(
        "python3 {}.py".format(
            os.path.join(project_dir, "src", "market_streaming_football")
        ),
        shell=True,
    )
while True:
    a = 1  # Do nothing
