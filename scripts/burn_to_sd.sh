#!/bin/bash

###############################################################################
## Functions
log() {
	echo -e "$(date +"%Y-%m-%dT%H:%M:%S.%03N") - $*"
}

help() {
	echo "Script used to burn a linux image to a SD."
	echo
	echo "Syntax:"
	echo "burn_to_sd.sh [-p <petalinux_directory] [-d <device path] [-h]"
	echo "options:"
	echo "-p|--project      Path to petalinux project."
	echo "-d|--device       Path to SD device."
	echo ""
}

parse_args() {
	if [ "$#" -eq 0 ]; then
		help
		exit 1
	fi

	while [ $# -gt 0 ]; do
		case "$1" in
		-h | --help)
			shift
			help
			;;
		-d | --device)
			shift
			DEVICE="${1}"
			shift
			;;
		-p | --project)
			shift
			LINUX_IMAGES_DIR="${1}/images/linux"
			shift
			;;
		*)
			echo "Invalid option: $1" >&2
			help
			exit 1
			;;
		esac
	done
}

check_prereq() {
	# Check if the script is run as root
	if [ "$EUID" -ne 0 ]; then
		log "Please run as root"
		exit 1
	fi
}

wipe() {
	# Wipe down the SD card
	read -p "WARNING: This will wipe all data on $DEVICE. Are you sure? (yes/no): " CONFIRM
	if [[ $CONFIRM != "yes" ]]; then
		log "Operation cancelled."
		exit 1
	fi

	log "Unmounting all partitions on $DEVICE..."
	umount ${DEVICE}* || log "No partitions to unmount"

	log "Wiping the $DEVICE..."
	dd if=/dev/zero of=${DEVICE} bs=512 count=1 status=progress
}

create_partitions() {
	log "Creating a new partition table on $DEVICE..."
	parted $DEVICE --script mklabel msdos

	log "Creating a new primary partition..."
	parted $DEVICE --script mkpart primary fat32 0% 100%

	PARTITION="${DEVICE}p1"
	log "Formatting the partition $PARTITION with FAT32..."
	mkfs.vfat -F 32 $PARTITION
}

copy_images() {
	MOUNT_POINT="/mnt/sdcard"
	log "Creating mount point at $MOUNT_POINT..."
	mkdir -p $MOUNT_POINT
	log "Mounting $PARTITION to $MOUNT_POINT..."
	mount $PARTITION $MOUNT_POINT

	rsync -av --progress --no-owner --no-group \
		"${LINUX_IMAGES_DIR}/BOOT.BIN" \
		"${LINUX_IMAGES_DIR}/boot.scr" \
		"${LINUX_IMAGES_DIR}/image.ub" \
		"${MOUNT_POINT}"

	umount ${PARTITION}
}

main() {
	check_prereq
	wipe
	create_partitions
	copy_images
}

parse_args "$@"
main
