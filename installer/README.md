# Petalinux installer

We are using this folder to store locally (not in the remote repository) some installers that are too big to use with git LFS.
For example, we are using in conjunction with `Dockerfile.petalinux_only_installer` to create a docker image layer with Petalinux installer.
So, if you want to re-build petalinux only installer docker image you should store here the `.run` from Xilinx and then run `./scripts/dockershell.sh -r -o` from the root of the repository.
