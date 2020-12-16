# pylint: disable=W0621

import json
import logging
import subprocess
import sys
from pathlib import Path

import pytest

current_dir = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent
logger = logging.getLogger(__name__)


def test_project_tree(cookies):
    result = cookies.bake(extra_context={"project_slug": "test_project"})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == "test_project"


@pytest.fixture(
    params=json.loads((current_dir / "../cookiecutter.json").read_text())["docker_base"]
)
def baked_project(cookies, request):
    return cookies.bake(
        extra_context={
            "project_slug": "DummyProject",
            "project_name": "dummy-project",
            "default_docker_registry": "test.test.com",
            "docker_base": request.param,
        }
    )


@pytest.mark.parametrize(
    "commands_on_baked_project",
    (
        "ls -la .",
        "make help",
        "make devenv",
        "make devenv; source .venv/bin/activate && make build up",
        "make devenv; source .venv/bin/activate && build-devel up-devel",
        "make info-build",
        "make devenv; source .venv/bin/activate && build tests",
    ),
)
def test_make_workflows(baked_project, commands_on_baked_project: str):
    working_dir = Path(baked_project.project)
    subprocess.run(
        ["/bin/bash", "-c", commands_on_baked_project], cwd=working_dir, check=True
    )
