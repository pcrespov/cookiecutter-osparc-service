# {{ cookiecutter.project_slug }}

{{ cookiecutter.project_short_description }}

## Usage

```console
$ make help

$ make devenv
$ source .venv/bin/activate

(.venv)$ make build
(.venv)$ make info-build
(.venv)$ make tests
```

## Workflow

1. The source code shall be copied to the [src]({{ cookiecutter.project_slug }}/src/{{ cookiecutter.project_package_name }}) folder.
1. The [Dockerfile]({{ cookiecutter.project_slug }}/src/Dockerfile) shall be modified to compile the source code.
2. The [metadata]({{ cookiecutter.project_slug }}/metadata) yaml file shall be modified to at least accomodate with the expected inputs/outputs of the service.
3. The [execute]({{ cookiecutter.project_slug }}/service.cli/execute) shell script shall be modified to run the service using the expected inputs and retrieve the expected outputs.
4. The test input/output shall be copied to [validation]({{ cookiecutter.project_slug }}/validation).
5. The service docker image may be built and tested as ``make build tests`` (see usage above)

## Versioning

Two versions:

- integration version (file VERSION) is updated with ``make version-integration-*``
- service version (file src/{{cookiecutter.project_package_name}}/VERSION) is updated with ``make version-service-*``

## CI/CD Integration

### Gitlab

add the following in your __gitlab-ci.yml__ file:

```yaml
include:
  - local: '/services/{{ cookiecutter.project_slug }}/ci/gitlab-ci.yml'
```
