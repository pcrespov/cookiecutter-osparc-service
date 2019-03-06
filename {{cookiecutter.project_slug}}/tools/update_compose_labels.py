###
# Usage: python update_compose_labels --c docker-compose.yml -f folder/path

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

import yaml


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
  for json_key, json_value in json_labels:
    if json_key in compose_labels:
      if compose_labels[json_key] == json_value:
        continue
    compose_labels[json_key] = json_value
    changed = True
  return changed

parser = argparse.ArgumentParser(
    description="Update a docker-compose file with json files in a path")
parser.add_argument(
    "--compose", help="The compose file where labels shall be updated", type=Path)
parser.add_argument("--input", help="The json folder to stringify", type=Path)
args = sys.argv[1:]
options = parser.parse_args(args)

try:
  # get available jsons
  compose_cfg = get_compose_file(options.compose)
  json_labels = stringify_folder(options.input)
  if update_compose_labels(compose_cfg, json_labels):
    # write the file back
    with options.compose.open('w') as fp:
      yaml.safe_dump(compose_cfg, fp)

except:
  sys.exit(1)

