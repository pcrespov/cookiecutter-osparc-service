#!/bin/sh
#
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -o errexit
set -o nounset

IFS=$(printf '\n\t')

# BOOTING application ---------------------------------------------
echo "Booting in ${SC_BOOT_MODE} mode ..."
echo   User    : "$(id "$(whoami)")"
echo   Workdir : "$(pwd)"


if [ "${SC_BUILD_TARGET}" = "development" ]
then
  echo "  Environment :"
  printenv  | sed 's/=/: /' | sed 's/^/    /' | sort
  #--------------------

elif [ "${SC_BUILD_TARGET}" = "production" ]
then
  echo "Target is ${SC_BUILD_TARGET}"
fi

/bin/sh