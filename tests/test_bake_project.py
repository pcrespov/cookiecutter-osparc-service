#pylint: disable=W0621

import logging
import os
import subprocess
from contextlib import contextmanager


logger = logging.getLogger(__name__)

@contextmanager
def inside_dir(dirpath):
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


def test_project_tree(cookies):
    result = cookies.bake(extra_context={'project_slug': 'test_project'})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == 'test_project'

def test_run_tests(cookies):
    result = cookies.bake(extra_context={'project_slug': 'dummy-project', 'default_docker_registry':'test.test.com'})
    working_dir = str(result.project)
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
    with inside_dir(working_dir):
        for cmd in commands:
            logger.info("Running '%s' ...", cmd)
            assert subprocess.run(cmd.split(), cwd=working_dir, check=True).returncode == 0
            logger.info("Done '%s' .", cmd)