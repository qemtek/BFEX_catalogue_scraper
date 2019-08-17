import os
import subprocess

from configuration import football
from configuration import project_dir
from configuration import racing

if racing:
    subprocess.call(
        "python3 {}.py".format(
            os.path.join(project_dir, "src", "market_streaming_racing")
        ),
        shell=True,
    )
if football:
    subprocess.call(
        "python3 {}.py".format(
            os.path.join(project_dir, "src", "market_streaming_football")
        ),
        shell=True,
    )
while True:
    a = 1  # Do nothing
