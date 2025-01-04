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


The step 2 can be done with a convenience script:

python3 scripts/petalinux_tales.py --xsa $(pwd)/xsa/minimal_system_wrapper.xsa --dir $(pwd)/work create-bsp --template zynq
