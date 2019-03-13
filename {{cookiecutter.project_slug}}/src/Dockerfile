FROM alpine:3.7 as base
#
#  USAGE:
#     cd services/{{ cookiecutter.project_slug }}
#     docker build -f Dockerfile -t {{ cookiecutter.project_slug }}:prod --target production ../../
#     docker run {{ cookiecutter.project_slug }}:prod
#

LABEL maintainer={{ cookiecutter.git_username }}

# simcore-user uid=8004(scu) gid=8004(scu) groups=8004(scu)
ENV SC_USER_ID 8004
ENV SC_USER_NAME scu
RUN adduser -D -u 8004 -s /bin/sh -h /home/scu scu

RUN apk add --no-cache \
      su-exec \
      bash \
      jq

# -------------------------- Build stage -------------------
# Installs build/package management tools and third party dependencies
#
# + /build             WORKDIR
#
{# SEE https://wiki.alpinelinux.org/wiki/Alpine_Linux_package_management #}
FROM base as build

ENV SC_BUILD_TARGET build

# ------------------------------------------------------------------------------------
#TODO:
# uncomment and adapt if build dependencies shall be installed
#RUN apk add --no-cache gcc git

# uncomment and adapt if python necessary
#RUN $SC_PIP install --upgrade pip wheel setuptools
# ------------------------------------------------------------------------------------

WORKDIR /build
# defines the output of the build
RUN mkdir -p /build/bin
# copy src code
COPY  src/{{ cookiecutter.project_package_name }} src/{{ cookiecutter.project_package_name }}
# ------------------------------------------------------------------------------------
#TODO:
# uncomment and adapt if build steps are necessary
# RUN gcc ...
# ------------------------------------------------------------------------------------

# --------------------------Cache stage -------------------
# CI in master buils & pushes this target to speed-up image build
#
#  + /build
#    + services/{{ cookiecutter.project_slug }} [scu:scu] WORKDIR
#
FROM build as cache

ENV SC_BUILD_TARGET cache

{# TODO: at the moment nothing is done here... its just a name #}

# --------------------------Production stage -------------------
# Final cleanup up to reduce image size and startup setup
# Runs as scu (non-root user)
#
#  + /home/scu     $HOME = WORKDIR
#    + {{ cookiecutter.project_package_name }} [scu:scu]
#    + docker [scu:scu]
#    + service.cli [scu:scu]
#
FROM base as production

ENV SC_BUILD_TARGET production
ENV SC_BOOT_MODE production

{% if cookiecutter.project_type == "computational" %}
ENV INPUT_FOLDER="/input" \
    OUTPUT_FOLDER="/output" \
    LOG_FOLDER="/log"
{% elif cookiecutter.project_type == "dynamic" %}
{# will not be necessary when the dy-sidecar comes in #}
ENV SIMCORE_NODE_UUID="-1" \
    SIMCORE_USER_ID="-1" \
    SIMCORE_NODE_BASEPATH="" \
    STORAGE_ENDPOINT="=1" \
    S3_ENDPOINT="=1" \
    S3_ACCESS_KEY="-1" \
    S3_SECRET_KEY="-1" \
    S3_BUCKET_NAME="-1" \
    POSTGRES_ENDPOINT="-1" \
    POSTGRES_USER="-1" \
    POSTGRES_PASSWORD="-1" \
    POSTGRES_DB="-1"
{%- endif %}

WORKDIR /home/scu

# ------------------------------------------------------------------------------------
#TODO:
# uncomment and adapt to install runtime dependencies
#RUN apk add --no-cache ffmpeg
# ------------------------------------------------------------------------------------

# copy binaries from cache
RUN mkdir -p {{ cookiecutter.project_package_name }} &&\
      chown scu:scu {{ cookiecutter.project_package_name }}
COPY --from=cache /build/bin {{ cookiecutter.project_package_name }}

# copy docker bootup scripts
COPY --chown=scu:scu docker/*.sh docker/
RUN chmod +x docker/*.sh

{%- if cookiecutter.project_type == "computational" %}
# copy simcore service cli
COPY --chown=scu:scu service.cli/ service.cli/
RUN chmod +x service.cli/*
# necessary to be able to call run directly without sh in front
ENV PATH="/home/scu/service.cli:${PATH}"
{%- endif %}

# ------------------------------------------------------------------------------------
#TODO:
# uncomment and provide a healtchecker if possible
# HEALTHCHECK --interval=30s \
#             --timeout=120s \
#             --start-period=30s \
#             --retries=3 \
#             CMD ["healthchecker app"]
# ------------------------------------------------------------------------------------

ENTRYPOINT [ "/bin/sh", "docker/entrypoint.sh" ]
CMD ["/bin/sh", "docker/boot.sh"]
