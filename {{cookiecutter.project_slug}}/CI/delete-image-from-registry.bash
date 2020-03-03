#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "deleting ${DOCKER_REGISTRY}/${DOCKER_PROJECT}"

DOCKER_TAG=$(./docker-registry-curl.bash https://"${DOCKER_REGISTRY}"/v2/"${DOCKER_PROJECT}"/tags/list | jq -r .tags[0])
while [ "${DOCKER_TAG}" != "null" ]
do
    echo "${DOCKER_PROJECT}:${DOCKER_TAG}..."
    DOCKER_ETAG=$(./docker-registry-curl.bash -I -H "Accept: application/vnd.docker.distribution.manifest.v2+json" -X GET "https://${DOCKER_REGISTRY}/v2/${DOCKER_PROJECT}/manifests/${DOCKER_TAG}" | grep -E "Docker-Content-Digest: " | cut -d " " -f2 | tr -d \" | sed 's/\r//')
    export DOCKER_ETAG
    ./docker-registry-curl.bash -X DELETE "https://${DOCKER_REGISTRY}/v2/${DOCKER_PROJECT}/manifests/${DOCKER_ETAG}"
    DOCKER_TAG=$(./docker-registry-curl.bash https://"${DOCKER_REGISTRY}"/v2/"${DOCKER_PROJECT}"/tags/list | jq -r .tags[0])
done
