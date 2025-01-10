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

# Wipe down the SD card
read -p "WARNING: This will wipe all data on $DEVICE. Are you sure? (yes/no): " CONFIRM
if [[ $CONFIRM != "yes" ]]; then
	echo "Operation cancelled."
	exit 1
fi

echo "Unmounting all partitions on $DEVICE..."
umount ${DEVICE}* || echo "No partitions to unmount"

echo "Wiping the $DEVICE..."
dd if=/dev/zero of=${DEVICE} bs=512 count=1 status=progress

echo "Creating a new partition table on $DEVICE..."
parted $DEVICE --script mklabel msdos

echo "Creating a new primary partition..."
parted $DEVICE --script mkpart primary fat32 0% 100%

PARTITION="${DEVICE}p1"
echo "Formatting the partition $PARTITION with FAT32..."
mkfs.vfat -F 32 $PARTITION

read -p "Do you want to mount the partition? (yes/no): " MOUNT_CONFIRM
if [[ $MOUNT_CONFIRM == "yes" ]]; then
	MOUNT_POINT="/mnt/sdcard"
	echo "Creating mount point at $MOUNT_POINT..."
	mkdir -p $MOUNT_POINT
	echo "Mounting $PARTITION to $MOUNT_POINT..."
	mount $PARTITION $MOUNT_POINT
	echo "SD card mounted at $MOUNT_POINT."
else
	echo "Skipping mounting step."
fi

echo "SD card formatted to FAT32 successfully."
