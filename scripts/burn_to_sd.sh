#!/bin/bash

###############################################################################
## Functions
log() {
	echo -e "$(date +"%Y-%m-%dT%H:%M:%S.%03N") - $*"
}

help() {
	echo "Script used to burn a linux image to a SD."
	echo "This will create 2 partitions in a SD:"
	echo "A first boot FAT32 partition where BOOT.BIN, image.ub and boot.src will be stored."
	echo "A second rootfs EXT4 partition where the rootfs will be extracted."
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
			PROJECT="${1}"
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

	# Define an array of variables
	variables=("DEVICE" "PROJECT")

	# Check if any variable is empty
	for var in "${variables[@]}"; do
		if [ -z "${!var}" ]; then
			echo "Variable $var is empty"
			exit 1
		fi
	done

	LINUX_IMAGES_DIR="${PROJECT}/images/linux"
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

	log "Creating a boot partition..."
	parted $DEVICE --script mkpart primary fat32 4MiB 1028MiB

	BOOT_PARTITION="${DEVICE}p1"
	log "Formatting the partition $BOOT_PARTITION with FAT32..."
	mkfs.vfat -n BOOT -F 32 $BOOT_PARTITION

	log "Creating a rootfs partition..."
	parted $DEVICE --script mkpart primary ext4 1028MiB 100%

	ROOTFS_PARTITION="${DEVICE}p2"
	log "Formatting the partition $ROOTFS_PARTITION with EXT4..."
	mkfs.ext4 -L RootFS $ROOTFS_PARTITION
}

copy_images() {
	MOUNT_POINT="/mnt/boot"
	log "Creating mount point at $MOUNT_POINT..."
	mkdir -p $MOUNT_POINT
	log "Mounting $BOOT_PARTITION to $MOUNT_POINT..."
	mount $BOOT_PARTITION $MOUNT_POINT

	rsync -av --progress --no-owner --no-group \
		"${LINUX_IMAGES_DIR}/BOOT.BIN" \
		"${LINUX_IMAGES_DIR}/boot.scr" \
		"${LINUX_IMAGES_DIR}/image.ub" \
		"${MOUNT_POINT}"

	umount ${BOOT_PARTITION}
}

copy_rootfs() {
	MOUNT_POINT="/mnt/rootfs"
	log "Creating mount point at $MOUNT_POINT..."
	mkdir -p $MOUNT_POINT
	log "Mounting $ROOTFS_PARTITION to $MOUNT_POINT..."
	mount $ROOTFS_PARTITION $MOUNT_POINT

	tar -xzf "${LINUX_IMAGES_DIR}/rootfs.tar.gz" -C ${MOUNT_POINT}

	umount ${ROOTFS_PARTITION}
}

main() {
	check_prereq
	wipe
	create_partitions
	copy_images
	copy_rootfs
}

parse_args "$@"
main
