#!/bin/bash
###############################################################################
## Function
log() {
	echo "$(date +"%Y-%m-%dT%H:%M:%S.%03N") - $*"
}

###############################################################################
## Parameters
DOCKER_IMAGE_EXECUTED_LOCALLY='petalinux_tales:local'
DOCKERFILE='Dockerfile.petalinux'
REBUILD_IMAGE=false

## Fixed variables
SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
RUN_CMD="docker run --rm -it -v $(pwd):/root/petalinux_tales ${DOCKER_IMAGE_EXECUTED_LOCALLY} /bin/bash"

while getopts "ro" opt; do
	case ${opt} in
	r)
		REBUILD_IMAGE=true
		;;
	o)
		DOCKER_IMAGE_EXECUTED_LOCALLY='petalinux_tales_only_installer:local'
		DOCKERFILE='Dockerfile.petalinux_only_installer'
		;;
	\?)
		echo "Invalid option: -$OPTARG"
		exit 1
		;;
	:)
		echo "The option -$OPTARG requires an argument."
		exit 1
		;;
	esac
done

log "SCRIPT_DIR = ${SCRIPT_DIR}"

if [ "${REBUILD_IMAGE}" = "true" ]; then
	log "erasing ${DOCKER_IMAGE_EXECUTED_LOCALLY}..."
	docker rmi -f ${DOCKER_IMAGE_EXECUTED_LOCALLY}
fi

if [[ "$(docker images -q ${DOCKER_IMAGE_EXECUTED_LOCALLY} 2>/dev/null)" == "" ]]; then
	log "${DOCKER_IMAGE_EXECUTED_LOCALLY} do no exists! building it..."
	docker build -f ${SCRIPT_DIR}/../docker/${DOCKERFILE} -t ${DOCKER_IMAGE_EXECUTED_LOCALLY} . &&
		${RUN_CMD}
else
	log "yeah! ${DOCKER_IMAGE_EXECUTED_LOCALLY} exists!!"
	${RUN_CMD}
fi
