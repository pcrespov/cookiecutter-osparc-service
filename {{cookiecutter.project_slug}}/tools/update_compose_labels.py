#!/bin/python

###
# Usage: python update_compose_labels --c docker-compose.yml -f folder/path

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict

import yaml

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_compose_file(compose_file: Path) -> Dict:
    with compose_file.open() as fp:
        return yaml.safe_load(fp)


def stringify_file(input_file: Path) -> str:
    with input_file.open() as fp:
        return json.dumps(json.load(fp))


def stringify_folder(folder: Path) -> Dict:
    jsons = {}
    for json_file in folder.glob("*.json"):
        jsons["io.simcore.{}".format(json_file.stem)] = stringify_file(json_file)
    return jsons


def update_compose_labels(compose_cfg: Dict, json_labels: Dict) -> bool:
  compose_labels = compose_cfg["services"]["{{ cookiecutter.project_slug }}"]["build"]["labels"]
  changed = False
  for json_key, json_value in json_labels.items():
    if json_key in compose_labels:
      if compose_labels[json_key] == json_value:
        continue
    compose_labels[json_key] = json_value
    changed = True
  return changed


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Update a docker-compose file with json files in a path")
  parser.add_argument(
      "--compose", help="The compose file where labels shall be updated", type=Path, required=True)
  parser.add_argument("--input", help="The json folder to stringify", type=Path, required=True)
  args = sys.argv[1:]
  options = parser.parse_args(args)

  try:
    log.info("Testing if %s needs updates using labels in %s", options.compose, options.input)
    # get available jsons
    compose_cfg = get_compose_file(options.compose)
    json_labels = stringify_folder(options.input)
    if update_compose_labels(compose_cfg, json_labels):
      log.info("Updating %s using labels in %s", options.compose, options.input)
      # write the file back
      with options.compose.open('w') as fp:
        yaml.safe_dump(compose_cfg, fp, default_flow_style=False)
        log.info("Update completed")
    else:
      log.info("No update necessary")
  except:
    log.exception("Unexpected error:")
    sys.exit(1)
