#!/bin/python

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_input_config(folder: Path) -> Dict:
    with (folder / "inputs.json").open() as fp:
        return json.load(fp)

def get_output_config(folder: Path) -> Dict:
    with (folder / "outputs.json").open() as fp:
        return json.load(fp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update the service.cli with given inputs/outputs")
    parser.add_argument("--folder", help="The json folder where to find the labels", type=Path, required=True)
    parser.add_argument("--runscript", help="The run script", type=Path, required=True)
    args = sys.argv[1:]
    options = parser.parse_args(args)

    # generate variables for input
    input_script = [
        "#!/bin/bash",
        "_json_input=$INPUT_FOLDER/input.json"
        ]
    input_config = get_input_config(options.folder)
    for input_key, input_value in input_config["inputs"].items():
        if "data:" in input_value["type"]:
            filename = input_key
            if "fileToKeyMap" in input_value and len(input_value["fileToKeyMap"] > 0):
                filename = input_value["fileToKeyMap"].values()[0]
            input_script.append("export {}=$INPUT_FOLDER/{}".format(str(Path(filename).stem).upper(), str(filename)))
        else:
            input_script.append("export {}=$(cat $_json_input | jq '.{}')".format(str(input_key).upper(), input_key))

    input_script.extend([
        "export LOG_FILE=$LOG_FOLDER/log.dat",
        "bash execute"
    ])

    # write shell script
    shell_script = str("\n").join(input_script)
    options.runscript.write_text(shell_script)


    output_config = get_output_config(options.folder)


