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
        "make build",
        "pip install -r tests/requirements.txt",
        "make unit-test",
        "make integration-test"
    )
    with inside_dir(working_dir):
        for cmd in commands:
            logger.info("Running '%s' ...", cmd)
            assert subprocess.check_call(cmd.split()) == 0
            logger.info("Done '%s' .", cmd)