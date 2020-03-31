cookiecutter-osparc-service
==========================================

Cookicutter to generate an oSparc compatible service for the oSparc simcore platform.

Status:

-------
Currently only for computational services. Work in progress.

![Build Status](https://github.com/ITISFoundation/cookiecutter-osparc-service/workflows/Github-CI%20Push/PR/badge.svg)

Requirements
------------

GNU Make
Python3

Install
------------

```console
git clone https://github.com/ITISFoundation/cookiecutter-osparc-service.git
cd cookiecutter-osparc-service
make devenv
source .venv/bin/activate
make play
```

Usage
-----

Generate a new Cookiecutter template layout: `cookiecutter gh:ITISFoundation/cookiecutter-osparc-service`

License
-------

This project is licensed under the terms of the [MIT License](/LICENSE)
