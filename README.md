# Petalinux Tales

In this repository you will find some utilities to build a PetaLinux image for Xilinx SoCs.

# Working with docker

The main idea is that we have a docker image with all the necessary tools.
We can create a local image and then enter to that shell using `scripts/dockershell.sh`.
Therefore, if we need to enter to that container in another terminal we can use: `docker exec -it <container_name> /bin/bash`. Be sure that you'll need to execute the entrypoint afterwards to have the environment ready: `source entrypoint.sh bash`.


