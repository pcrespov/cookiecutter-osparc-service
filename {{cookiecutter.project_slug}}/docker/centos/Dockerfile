FROM {{ cookiecutter.docker_base }} as base
#
#  USAGE:
#     cd services/{{ cookiecutter.project_slug }}
#     docker build -f Dockerfile -t {{ cookiecutter.project_slug }}:prod --target production ../../
#     docker run {{ cookiecutter.project_slug }}:prod
#

LABEL maintainer={{ cookiecutter.git_username }}

# simcore-user uid=8004(${SC_USER_NAME}) gid=8004(${SC_USER_NAME}) groups=8004(${SC_USER_NAME})
ENV SC_USER_ID 8004
ENV SC_USER_NAME scu
ENV SC_GROUP_ID ${SC_USER_ID}
ENV SC_GROUP_NAME ${SC_USER_NAME}


RUN groupadd --gid ${SC_GROUP_ID} ${SC_GROUP_NAME}
RUN useradd -d /home/${SC_USER_NAME} --uid ${SC_USER_ID} --gid ${SC_GROUP_ID} --shell /bin/sh ${SC_USER_NAME}

RUN yum -y install epel-release && \
    yum -y install \
    jq && \
    yum clean all && \
    rm -rf /var/cache/yum

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
#RUN yum -y install \
#    gcc \
#    gcc-c++ \
#    git \
#    yum clean all && \
#    rm -rf /var/cache/yum

# ------------------------------------------------------------------------------------

WORKDIR /build
# defines the output of the build
RUN mkdir --parents /build/bin
# copy src code
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} src/{{ cookiecutter.project_package_name }} src/{{ cookiecutter.project_package_name }}
# ------------------------------------------------------------------------------------
#TODO:
# uncomment and adapt if build steps are necessary
# RUN cp -R src/{{ cookiecutter.project_package_name }}/* /build/bin
# ------------------------------------------------------------------------------------

# --------------------------Production stage -------------------
# Final cleanup up to reduce image size and startup setup
# Runs as ${SC_USER_NAME} (non-root user)
#
#  + /home/${SC_USER_NAME}     $HOME = WORKDIR
#    + {{ cookiecutter.project_package_name }} [${SC_USER_NAME}:${SC_USER_NAME}]
#    + docker [${SC_USER_NAME}:${SC_USER_NAME}]
#    + service.cli [${SC_USER_NAME}:${SC_USER_NAME}]
#
FROM base as production

ENV SC_BUILD_TARGET production
ENV SC_BOOT_MODE production

{% if cookiecutter.project_type == "computational" %}
ENV INPUT_FOLDER="/input" \
    OUTPUT_FOLDER="/output"
{% elif cookiecutter.project_type == "dynamic" %}
{# will not be necessary when the dy-sidecar comes in #}
ENV SIMCORE_NODE_UUID="-1" \
    SIMCORE_USER_ID="-1" \
    SIMCORE_NODE_BASEPATH="" \
    STORAGE_ENDPOINT="=1" \
    POSTGRES_ENDPOINT="-1" \
    POSTGRES_USER="-1" \
    POSTGRES_PASSWORD="-1" \
    POSTGRES_DB="-1"
{%- endif %}

WORKDIR /home/${SC_USER_NAME}

# ------------------------------------------------------------------------------------
#TODO:
# uncomment and adapt to install runtime dependencies
#RUN yum -y install \
#    yum clean all && \
#    rm -rf /var/cache/yum
# ------------------------------------------------------------------------------------

# copy docker bootup scripts
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} docker/{{ cookiecutter.docker_base.split(":")[0] }}/*.sh docker/

{%- if cookiecutter.project_type == "computational" %}
# copy simcore service cli
COPY --chown=${SC_USER_NAME}:${SC_USER_NAME} service.cli/ service.cli/
# necessary to be able to call run directly without sh in front
ENV PATH="/home/${SC_USER_NAME}/service.cli:${PATH}"
{%- endif %}

# copy binaries from build
COPY --from=build --chown=${SC_USER_NAME}:${SC_USER_NAME} /build/bin {{ cookiecutter.project_package_name }}

# ------------------------------------------------------------------------------------
#TODO:
# uncomment and provide a healtchecker if possible
# HEALTHCHECK --interval=30s \
#             --timeout=120s \
#             --start-period=30s \
#             --retries=3 \
#             CMD ["healthchecker app"]
# ------------------------------------------------------------------------------------

ENTRYPOINT [ "/bin/sh", "docker/entrypoint.sh", "/bin/sh", "-c" ]
CMD ["run"]
