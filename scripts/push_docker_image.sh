#!/bin/bash
###############################################################################
## Function
log() {
	echo "$(date +"%Y-%m-%dT%H:%M:%S.%03N") - $*"
}

###############################################################################
## Parameters
DOCKER_IMAGE='petalinux_tales'
DOCKERFILE='Dockerfile.petalinux'
TAG=''
REPOSITORY='marifante/petalinux_tales'
USERNAMEA="marifante"

## Fixed variables
SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

while [[ $# -gt 0 ]]; do
	case "$1" in
	-o)
		DOCKER_IMAGE='petalinux_tales_only_installer'
		DOCKERFILE='Dockerfile.petalinux_only_installer'
		;;
	--tag)
		if [[ -n "$2" ]]; then
			TAG=$2
			shift 2
		else
			log "Error: --tag requires a value." >&2
			exit 1
		fi
		;;
	--token)
		if [[ -n "$2" ]]; then
			TOKEN=$2
			shift 2
		else
			log "Error: --token requires a value." >&2
			exit 1
		fi
		;;
	--username)
		if [[ -n "$2" ]]; then
			USERNAME=$2
			shift 2
		else
			log "Error: --username requires a value." >&2
			exit 1
		fi
		;;
	--repository)
		if [[ -n "$2" ]]; then
			REPOSITORY=$2
			shift 2
		else
			log "Error: --repository requires a value." >&2
			exit 1
		fi
		;;
	*)
		echo "Unknown argument: $1" >&2
		exit 1
		;;
	esac
done

# Store arguments in an array
INPUTS_TO_VERIFY=("TOKEN" "REPOSITORY" "REPOSITORY" "USERNAME" "TAG")

# Loop through arguments and check if they are empty
for arg in "${INPUTS_TO_VERIFY[@]}"; do
	if [[ -z "${!arg}" ]]; then
		echo "Error: $arg is empty!"
		exit 1
	fi
done

echo "${TOKEN}" | docker login ghcr.io -u ${USERNAME} --password-stdin

docker push ghcr.io/${REPOSITORY}/${DOCKER_IMAGE}:${TAG}
