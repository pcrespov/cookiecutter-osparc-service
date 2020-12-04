#pylint: disable=W0621

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

import pytest

# current directory
current_dir = Path(sys.argv[0] if __name__ ==
                   "__main__" else __file__).resolve().parent

logger = logging.getLogger(__name__)


def test_project_tree(cookies):
    result = cookies.bake(extra_context={'project_slug': 'test_project'})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == 'test_project'


def _get_cookiecutter_config() -> Dict:
    cookiecutter_config_file = current_dir / "../cookiecutter.json"
    with cookiecutter_config_file.open() as fp:
        return json.load(fp)


flavors = _get_cookiecutter_config()["docker_base"]


@pytest.fixture(params=flavors)
def baked_project(cookies, request):
    return cookies.bake(extra_context={'project_slug': 'dummy-project', 'default_docker_registry': 'test.test.com', 'docker_base': request.param})


commands = (
    "ls -la .",
    "make help",
    "make devenv",
    "make devenv; source .venv/bin/activate; make build up",
    "make devenv; source .venv/bin/activate; build-devel up-devel",
    "make info-build",
    "make devenv; source .venv/bin/activate; build tests",
)


@pytest.mark.parametrize("command", commands)
def test_run_tests(baked_project, command: str):
    working_dir = Path(baked_project.project)

    if ";" in command:
        script_path = working_dir / "script.bash"
        with open(script_path, "wt") as fh:
            print("#!/bin/bash", file=fh)
            print("# strict mode", file=fh)
            print("set - o errexit   # abort on nonzero exitstatus", file=fh)
            print("set - o nounset   # abort on unbound variable", file=fh)
            print("set - o pipefail  # don't hide errors within pipes", file=fh)
            print("IFS =$'\n\t'", file=fh)
            print("")
            for line in command.split(";"):
                print(line.strip(), file=fh)
        print(script_path, "-"*50)
        print(script_path.read_text())
        assert subprocess.run(["/bin/bash", script_path.name], cwd=working_dir,
                              check=True).returncode == 0
    else:
        assert subprocess.run(command.split(), cwd=working_dir,
                              check=True).returncode == 0
