# {{ cookiecutter.project_slug }}

{{ cookiecutter.project_short_description }}

## Development

```console
make help
```

Standard dev workflow is

``` console
make venv
source .venv/bin/activate

(.venv)$ make requirements
(.venv)$ make install
(.venv)$ make test
```
