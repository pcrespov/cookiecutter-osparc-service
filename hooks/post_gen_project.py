import shutil
import sys
from pathlib import Path

selected_flavor = '{{ cookiecutter.docker_base }}'

try:
    folder_name = Path("docker") / selected_flavor.split(":")[0]

    # list folders
    # NOTE: it needs to be a list as we delete the folders
    for folder in list(Path("docker").glob("*/**")):
        if folder.exists() and folder != folder_name:
            shutil.rmtree(folder)
except Exception as exc:  # pylint: disable=broad-except
    print(exc)
    sys.exit(1)
