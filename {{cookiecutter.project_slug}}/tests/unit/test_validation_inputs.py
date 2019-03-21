# pylint:disable=wildcard-import
# pylint:disable=unused-import
# pylint:disable=unused-variable
# pylint:disable=unused-argument
# pylint:disable=redefined-outer-name
import json
from pathlib import Path
from typing import Dict

import pytest


@pytest.fixture
def inputs_cfg(docker_dir: Path) -> Dict:
    inputs_file = docker_dir / "labels" / "inputs.json"
    assert inputs_file.exists()
    with inputs_file.open() as fp:
        input_cfg = json.load(fp)
        assert "inputs" in input_cfg
        return input_cfg["inputs"]

@pytest.fixture
def validation_input_cfg(validation_dir: Path) -> Dict:
    validation_input_file = validation_dir / "input" / "input.json"
    assert validation_input_file.exists()

    with validation_input_file.open() as fp:
        return json.load(fp)


def _find_key_in_inputs(filename: str, value: Dict) -> str:
    for k, v in value.items():
        if k == filename:
            if isinstance(v, dict):
                assert "data:" in v["type"]
                yield k
            else:                
                yield v
        elif isinstance(v, dict):
            for result in _find_key_in_inputs(filename, v):
                yield result
        

def test_validation_input_follows_definition(inputs_cfg: Dict, validation_input_cfg: Dict, validation_dir: Path):
    for key, value in inputs_cfg.items():
        assert "type" in value
        # rationale: files are on their own and other types are in input.json
        if not "data:" in value["type"]:
            # check that keys are available
            assert key in validation_input_cfg
        else:
            # it's a file and it should be in the folder as well using key as the filename
            filename_to_look_for = key
            if "fileToKeyMap" in value:
                # ...or there is a mapping
                assert len(value["fileToKeyMap"]) > 0
                for filename, mapped_value in value["fileToKeyMap"].items():
                    assert mapped_value == key
                    filename_to_look_for = filename
                    assert (validation_dir / "input" / filename_to_look_for).exists()

    for key, value in validation_input_cfg.items():
        # check the key is defined in the inputs
        assert key in inputs_cfg
        types = {"number": (float, int), "integer": int, "boolean": bool, "string": str}
        if not "data:" in inputs_cfg[key]["type"]:
            # check the type is correct
            assert isinstance(value, types[inputs_cfg[key]["type"]])
    
    validation_input_folder = validation_dir / "input"
    for path in validation_input_folder.glob("**/*"):
        if path.name in ["input.json", ".gitkeep"]:
            continue
        assert path.is_file()
        filename = path.name
        # this filename shall be available as a key in the inputs.json somewhere
        key = next(_find_key_in_inputs(str(filename), inputs_cfg))

        assert key in inputs_cfg
