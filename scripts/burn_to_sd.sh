#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
	echo "Please run as root"
	exit 1
fi

# Check if the device is provided
if [ -z "$1" ]; then
	echo "Usage: $0 /dev/sdX"
	exit 1
fi

DEVICE=$1

# Unmount the device
umount ${DEVICE}* || echo "No partitions to unmount"

# Create a new partition table
parted $DEVICE mklabel msdos

# Create a primary partition
parted -a optimal $DEVICE mkpart primary fat32 0% 100%

# Format the partition to FAT32
mkfs.vfat -F 32 ${DEVICE}1

echo "SD card formatted to FAT32 successfully."
