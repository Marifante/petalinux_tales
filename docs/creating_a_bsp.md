# Creating a BSP

A BSP (Board Support Package) should contain all the features for the **board** that we will be using.
For example, if we'll use the Arty Z7 devkit, we should have a BSP for that board.
It contains:
* The device-tree
* The kernel configuration
* The U-Boot configuration

To create a BSP we should do the following:
1) Create and export hardware design (HDF/XSA) from Vivado
2) Create a blank PetaLinux project without a BSP
3) Customize the blank PetaLinux project to fit our needs
4) Package that PetaLinux project into a BSP
5) Test the BSP by creating a new project.


Steps 2 to 4 can be done using a convenience script:

petalinux_tales create-bsp --xsa xsa/artyz710_minimal_system_wrapper.xsa --dir work --template zynq --output bsp/new_bsp.bsp

This script will create a blank Petalinux project with a given template, then will allow the user to modify that BSP and when the user is done will build it and package it into a BSP.
During the process, the following output files will be created in work directory:
* ${WORK_DIRECTORY}/images/linux/BOOT.BIN
* ${WORK_DIRECTORY}/images/linux/image.ub
* ${WORK_DIRECTORY}/images/linux/boot.scr
* ${WORK_DIRECTORY}/images/linux/rootfs.tar.gz

If you want to directly use this BSP to boot a linux in the device, you should copy BOOT.BIN, image.ub and boot.scr to boot partition of the micro SD. Also, you will need to extract rootfs.tar.gz file into rootfs partition.
There is a convenience script in `scripts/burn_to_sd.sh` that takes care of this part of the process. That script will format the SD and copy all the necessary files.

