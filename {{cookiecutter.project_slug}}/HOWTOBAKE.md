# {{ cookiecutter.project_slug }} - How to Bake your Cookie

{{ cookiecutter.project_short_description }}

## Development

1. The source code shall be copied to the [src]({{ cookiecutter.project_slug }}/src/{{ cookiecutter.project_package_name }}) folder.
2. The [Dockerfile]({{ cookiecutter.project_slug }}/src/Dockerfile) shall be modified to compile the source code.
3. The [labels]({{ cookiecutter.project_slug }}/docker/labels) json files shall be modified to at least accomodate with the expected inputs/outputs of the service.
4. The [execute]({{ cookiecutter.project_slug }}/service.cli/execute) bash script shall be modified to run the service using the expected inputs and retrieve the expected outputs and log.
5. The test input/output/log shall be copied to [validation]({{ cookiecutter.project_slug }}/validation).
6. The service docker image may be built and tested using:

``` console
make .venv
source .venv/bin/activate

(.venv)$ make build
(.venv)$ make unit-test
(.venv)$ make integration-test
```

## Usage

Default usage will build the service inside a docker container and then run the service using the validation data as input by default.
Results will be stored in {{ cookiecutter.project_slug }}/tmp/output and logs in {{ cookiecutter.project_slug }}/tmp/log.

```console
make .venv
source .venv/bin/activate

(.venv)$ make build
(.venv)$ make up
```

## CI/CD Integration

### Gitlab

add the following in your __gitlab-ci.yml__ file:

```yaml
include:
  - local: '/models/{{ cookiecutter.project_slug }}/CI/gitlab-ci.yml'
```
