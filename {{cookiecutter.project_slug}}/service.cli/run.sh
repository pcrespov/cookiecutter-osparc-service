#!/bin/sh
# Alpine linux default shell is sh, this is a trick to call a bash script
set -o errexit
set -o nounset

IFS=$(printf '\n\t')

exec do_run.bash
