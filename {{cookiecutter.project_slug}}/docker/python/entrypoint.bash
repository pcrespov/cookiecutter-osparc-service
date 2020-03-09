#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

IFS=$'\n\t'
# This entrypoint script:
#
# - Executes *inside* of the container upon start as --user [default root]
# - Notice that the container *starts* as --user [default root] but
#   *runs* as non-root user [$SC_USER_NAME]
#
echo Entrypoint for stage "${SC_BUILD_TARGET}" ...
echo   User    : "$(id "$(whoami)")"
echo   Workdir : "$(pwd)"


# expect input/output folders to be mounted
stat "${INPUT_FOLDER}" > /dev/null 2>&1 || \
        (echo "ERROR: You must mount '${INPUT_FOLDER}' to deduce user and group ids" && exit 1)
stat "${OUTPUT_FOLDER}" > /dev/null 2>&1 || \
    (echo "ERROR: You must mount '${OUTPUT_FOLDER}' to deduce user and group ids" && exit 1)

# NOTE: expects docker run ... -v /path/to/input/folder:${INPUT_FOLDER}
# check input/output folders are owned by the same user
if [ "$(stat -c %u "${INPUT_FOLDER}")" -ne "$(stat -c %u "${OUTPUT_FOLDER}")" ]
then
    echo "ERROR: '${INPUT_FOLDER}' and '${OUTPUT_FOLDER}' have different user id's. not allowed" && exit 1
fi
# check input/outputfolders are owned by the same group
if [ "$(stat -c %g "${INPUT_FOLDER}")" -ne "$(stat -c %g "${OUTPUT_FOLDER}")" ]
then
    echo "ERROR: '${INPUT_FOLDER}' and '${OUTPUT_FOLDER}' have different group id's. not allowed" && exit 1
fi

echo "setting correct user id/group id..."
USERID=$(stat --format=%u "${INPUT_FOLDER}")
GROUPID=$(stat --format=%g "${INPUT_FOLDER}")
GROUPNAME=$(getent group "${GROUPID}" | cut --delimiter=: --fields=1)
if [ "$USERID" -eq 0 ]
then
    echo "Warning: Folder mounted owned by root user... adding $SC_USER_NAME to root..."
    adduser "$SC_USER_NAME" root
else
    echo "Folder mounted owned by user $USERID:$GROUPID-'$GROUPNAME'..."
    # take host's credentials in $SC_USER_NAME
    if [ -z "$GROUPNAME" ]
    then
        echo "Creating new group my$SC_USER_NAME"
        GROUPNAME=my$SC_USER_NAME
        addgroup --gid "$GROUPID" "$GROUPNAME"
        # change group property of files already around
        find / -path /proc -prune -group "$SC_USER_ID" -exec chgrp --no-dereference "$GROUPNAME" {} \;
    else
        echo "adding $SC_USER_NAME to group $GROUPNAME..."
        adduser "$SC_USER_NAME" "$GROUPNAME"
    fi

    echo "changing $SC_USER_NAME $SC_USER_ID:$SC_USER_ID to $USERID:$GROUPID"
    deluser "$SC_USER_NAME" > /dev/null 2>&1
    if [ "$SC_USER_NAME" = "$GROUPNAME" ]
    then
        addgroup --gid "$GROUPID" "$GROUPNAME"
    fi
    adduser --disabled-password --gecos "" --uid "$USERID" --gid "$GROUPID" --shell /bin/bash "$SC_USER_NAME" --no-create-home
    # change user property of files already around
    find / -user "$SC_USER_ID" -exec chown --no-dereference "$SC_USER_NAME" {} \;
fi

echo "Starting $* ..."
echo "  $SC_USER_NAME rights    : $(id "$SC_USER_NAME")"
echo "  local dir : $(ls -al)"
echo "  input dir : $(ls -al "${INPUT_FOLDER}")"
echo "  output dir : $(ls -al "${OUTPUT_FOLDER}")"

su --preserve-environment --command "export PATH=${PATH}:/home/$SC_USER_NAME/service.cli; $*" "$SC_USER_NAME"