#!/bin/bash
###############################################################################
## Function
log() {
	echo "$(date +"%Y-%m-%dT%H:%M:%S.%03N") - $*"
}

###############################################################################
## Parameters
DOCKER_IMAGE_EXECUTED_LOCALLY='petalinux_tales:local'
REBUILD_IMAGE=false

## Fixed variables
SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
RUN_CMD="docker run --rm -it -v $(pwd):/petalinux_tales ${DOCKER_IMAGE_EXECUTED_LOCALLY} /bin/bash"

while getopts "r" opt; do
	case ${opt} in
	r)
		REBUILD_IMAGE=true
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
	docker build -f ${SCRIPT_DIR}/../docker/Dockerfile.petalinux -t ${DOCKER_IMAGE_EXECUTED_LOCALLY} . &&
		${RUN_CMD}
else
	log "yeah! ${DOCKER_IMAGE_EXECUTED_LOCALLY} exists!!"
	${RUN_CMD}
fi
