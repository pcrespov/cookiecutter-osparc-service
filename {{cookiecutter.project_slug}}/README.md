# {{ cookiecutter.project_slug }}

{{ cookiecutter.project_short_description }}

## Development

```console
$ make help
```

Standard dev workflow is
``` console
$ make venv
$ source .venv/bin/activate

(.venv)$ make requirements
(.venv)$ make install

(.venv)$ make test
```
To start the service just check (some config files under ``{{cookiecutter.project_slug}}/src/{{cookiecutter.package_name}}/config`` )
```
$ {{ cookiecutter.command_line_interface_bin_name }} --help

$ {{ cookiecutter.command_line_interface_bin_name }} --config config-host-dev.yml
```
