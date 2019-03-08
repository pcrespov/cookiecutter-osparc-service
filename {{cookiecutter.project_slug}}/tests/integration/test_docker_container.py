# pylint:disable=wildcard-import
# pylint:disable=unused-import
# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name

import filecmp
import shutil
from pathlib import Path
from typing import Dict

import docker
import pytest


@pytest.fixture
def docker_client() -> docker.DockerClient:
    return docker.from_env()

@pytest.fixture
def docker_image_key(docker_client: docker.DockerClient) -> str:
    image_key = "simcore/services/{%- if cookiecutter.project_type == 'computational' -%}comp{%- elif cookiecutter.project_type == 'dynamic' -%}dynamic{%- endif -%}/{{ cookiecutter.project_name.lower().replace(' ', '-') }}:latest"
    docker_images = [image for image in docker_client.images.list() if any(image_key in tag for tag in image.tags)]
    assert len(docker_images) == 1
    assert image_key in docker_images[0].tags[0]
    return docker_images[0].tags[0]

@pytest.fixture
def host_folders(tmp_path) -> Dict:
    host_input_dir = tmp_path / "input"
    host_input_dir.mkdir()
    host_output_dir = tmp_path / "output"
    host_output_dir.mkdir()
    host_log_dir = tmp_path / "log"
    host_log_dir.mkdir()
    return {"input":host_input_dir, "output":host_output_dir, "log":host_log_dir}

@pytest.fixture
def container_variables() -> Dict:
    env_variables = {
        "INPUT_FOLDER": "/input",
        "OUTPUT_FOLDER": "/output",
        "LOG_FOLDER": "/log"
    }
    return env_variables

@pytest.fixture
def validation_folders(validation_dir: Path) -> Dict:
    input_folder = validation_dir / "input"
    assert input_folder.exists()
    output_folder = validation_dir / "output"
    assert output_folder.exists()
    log_folder = validation_dir / "log"
    assert log_folder.exists()
    return {"input":input_folder, "output":output_folder, "log":log_folder}

def test_run_container(validation_folders: Dict, host_folders: Dict, docker_client: docker.DockerClient, docker_image_key: str, container_variables: Dict):
    # copy file to input folder
    host_folders["input"].rmdir()
    shutil.copytree(validation_folders["input"], host_folders["input"])
    assert Path(host_folders["input"]).exists()
    # run the container (this may take some time)
    docker_client.containers.run(docker_image_key,
        "run", detach=False, remove=True,
        volumes = {
            host_folders["input"] : {
                'bind' : container_variables["INPUT_FOLDER"],
                'mode': 'ro'
                },
            host_folders["output"] : {
                'bind' : container_variables["OUTPUT_FOLDER"],
                'mode': 'rw'
                },
            host_folders["log"] : {
                'bind': container_variables["LOG_FOLDER"],
                'mode': 'rw'
                }
            },
        environment=container_variables)

    for folder in ["input", "output", "log"]:
        # test if the files that should be there are actually there and correct
        list_of_files = [x.name for x in validation_folders[folder].iterdir()]
        match, mismatch, errors = filecmp.cmpfiles(host_folders[folder], validation_folders[folder], list_of_files, shallow=False)
        assert not mismatch, "wrong/incorrect files in {}".format(host_folders[folder])
        assert not errors, "missing files in {}".format(host_folders[folder])
        # test if the files that are there are matching the ones that should be
        list_of_files = [x.name for x in host_folders[folder].iterdir()]
        match, mismatch, errors = filecmp.cmpfiles(host_folders[folder], validation_folders[folder], list_of_files, shallow=False)
        assert not mismatch, "wrong/incorrect generated files in {}".format(host_folders[folder])
        assert not errors, "too many files in {}".format(host_folders[folder])
