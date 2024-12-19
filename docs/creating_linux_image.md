# Creating Linux Image

The goal of this section is to generate the petalinux boot images (BOOT.bin and image.ub).

## BOOT.bin

The BOOT.bin file can be put into a Flash or SD card. Then, when you power on the board it can boot from the boot image.
Usually, a boot image contains:
* the first stage boot loader image
* FPGA bitstream
* PMU firmware: the Power Management Unit is a hardware block responsible for managing and controlling the power usage of different components in the system.
* TF-A (Trusted Firmware-A): an open-source reference implementation of Arm's Trusted Execution Environment (TEE) architecture. It is designed to provide secure initialization and runtime services on Arm-based platforms.
* U-Boot: bootloader that initializes the hardware (like the CPU, memory, and storage) and loads the operating system into memory.

## Inputs

In order to generate BOOT.bin we nee the following files:

* Hardware XSA (Xilinx System Archive): this is a file obtained from Vivado. It contains the hardware configuration (peripherals, processor configurations, memory mappings, clock configurations, etc), device tree fragments, address maps, etc.
* The BSP (Board Support Package)

## Reference

* https://xilinx.github.io/Embedded-Design-Tutorials/docs/2021.1/build/html/docs/Introduction/Zynq7000-EDT/4-linux-for-zynq.html
* https://www.xilinx.com/support/documents/sw_manuals/xilinx2022_2/ug1144-petalinux-tools-reference-guide.pdf
