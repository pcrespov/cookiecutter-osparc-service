FROM alpine as base
#
#  USAGE:
#     cd sercices/{{ cookiecutter.project_slug }}
#     docker build -f Dockerfile -t {{ cookiecutter.project_slug }}:prod --target production ../../
#     docker run {{ cookiecutter.project_slug }}:prod
#

LABEL maintainer={{ cookiecutter.github_username }}

# simcore-user uid=8004(scu) gid=8004(scu) groups=8004(scu)
RUN adduser -D -u 8004 -s /bin/sh -h /home/scu scu

RUN apk add --no-cache \
      su-exec

# -------------------------- Build stage -------------------
# Installs build/package management tools and third party dependencies
#
# + /build             WORKDIR
#
{# SEE https://wiki.alpinelinux.org/wiki/Alpine_Linux_package_management
#  SEE https://pip.pypa.io/en/stable/reference/pip_install #}
FROM base as build

ENV SC_BUILD_TARGET build

# uncomment and adapt if build dependencies shall be installed
#RUN apk add --no-cache gcc git

# uncomment and adapt if python necessary
#RUN $SC_PIP install --upgrade pip wheel setuptools

WORKDIR /build
# defines the output of the build
VOLUME /build/bin
# copy src code
COPY  src/{{ cookiecutter.project_package_name }} src/{{ cookiecutter.project_package_name }}
# uncomment and adapt if build steps are necessary
# RUN gcc ...

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
#
FROM base as production

ENV SC_BUILD_TARGET production
ENV SC_BOOT_MODE production

WORKDIR /home/scu

# uncomment and adapt to install runtime dependencies
#RUN apk add --no-cache ffmpeg
# copy binaries from cache
RUN mkdir -p {{ cookiecutter.project_package_name }} &&\
      chown scu:scu {{ cookiecutter.project_package_name }}
COPY --from=cache /build/bin {{ cookiecutter.project_package_name }}

# copy docker bootup scripts
COPY --chown=scu:scu docker/*.sh docker/

# uncomment and provide a healtchecker if possible
# HEALTHCHECK --interval=30s \
#             --timeout=120s \
#             --start-period=30s \
#             --retries=3 \
#             CMD ["healthchecker app"]

ENTRYPOINT [ "/bin/sh", "docker/entrypoint.sh" ]
CMD ["/bin/sh", "docker/boot.sh"]
