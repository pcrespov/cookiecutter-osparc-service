#pylint: disable=W0621

import logging
import os
import subprocess
from pathlib import Path
import pytest

logger = logging.getLogger(__name__)

def test_project_tree(cookies):
    result = cookies.bake(extra_context={'project_slug': 'test_project'})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == 'test_project'


@pytest.fixture(scope="module")
def baked_project(cookies):
    return cookies.bake(extra_context={'project_slug': 'dummy-project', 'default_docker_registry':'test.test.com'})

commands = (
        "ls -la .",
        "make help",
        "make devenv",
        "make build",
        "make build-devel",
        "make info-build",
        "make tests-unit",
        "make tests-integration"
    )

@pytest.mark.parametrize("command", commands)
def test_run_tests(baked_project, command: str):
    working_dir = Path(baked_project.project)
    assert subprocess.run(command.split(), cwd=working_dir, check=True).returncode == 0
