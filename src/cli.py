import argparse


from petalinux_tales.log import setup_logger
from petalinux_tales.bsp_creator import PetaLinuxBSPCreator
from petalinux_tales.image_creator import PetalinuxImageCreator


logger = setup_logger(__name__)


def parse_args():
    """ Parse input arguments """
    parser = argparse.ArgumentParser(description="Create a Linux Image for a target board.")
    parser.add_argument('-x', '--xsa', type = str, required = True, help = "Path to board's XSA")
    parser.add_argument('-d', '--dir', type = str, default = "work", help = "Work directory")
    parser.add_argument('-p', '--install-dir', type = str, default = "/home/embeddev/petalinux", help = "Petalinux install dir")

    subparsers = parser.add_subparsers(dest='mode', required=True, help='Chose a mode')

    parser_from_bsp = subparsers.add_parser('from-bsp', help='Create a Linux image using a BSP as a base')
    parser_from_bsp.add_argument('-b', '--bsp', type = str, required = True, help = "Path to board's BSP")

    parser_create_bsp = subparsers.add_parser('create-bsp', help='Create a BSP from a blank PetaLinux project')
    parser_create_bsp.add_argument('-t', '--template', type = str, required = True, help = "Path to board's BSP")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    common_args = {
        "xsa_path": args.xsa, "dir": args.dir, "install_dir": args.install_dir
    }

    if 'from-bsp' == args.mode:
        creator = PetalinuxImageCreator(args.bsp, **common_args)
    elif 'create-bsp' == args.mode:
        creator = PetaLinuxBSPCreator(args.template, **common_args)
    else:
        raise NotImplementedError(f"Mode {args.mode} is not implemented!")

    creator.run()
