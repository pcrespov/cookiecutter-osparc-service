# cookiecutter-osparc-service

Status: ![Build Status](https://github.com/ITISFoundation/cookiecutter-osparc-service/workflows/Github-CI%20Push/PR/badge.svg)


Cookiecutter to generate an oSparc compatible service for the oSparc simcore platform. Currently only for **computational services**.


## Requirements


GNU Make
Python3
Python3-venv
cookiecutter python package
```console
sudo apt-get update
sudo apt-get install -y make python3-venv   # install GNU Make, python3-venv (python3 is usually already installed)
python3 -m venv .venv                       # create a python virtual environment
source .venv/bin/activate                   # activate the python virtual environment
pip install cookiecutter                    # install the cookicutter package
```

## Usage

Generate a new Cookiecutter template layout:
```console
python3 -m venv .venv                                          # create a python virtual environment
source .venv/bin/activate                                      # activate the python virtual environment
cookiecutter gh:ITISFoundation/cookiecutter-osparc-service     # generate a cookie (use cookiecutter --help for additional options)
```




## Development

```console
git clone https://github.com/ITISFoundation/cookiecutter-osparc-service.git
cd cookiecutter-osparc-service
make devenv
source .venv/bin/activate
make play
```

## Testing

```console
git clone https://github.com/ITISFoundation/cookiecutter-osparc-service.git
cd cookiecutter-osparc-service
make devenv
source .venv/bin/activate
make tests
```




## License

This project is licensed under the terms of the [MIT License](/LICENSE)


---

<p align="center">
<img src="https://forthebadge.com/images/badges/built-with-love.svg" width="150">
</p>
