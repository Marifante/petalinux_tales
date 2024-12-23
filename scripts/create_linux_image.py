import argparse
import logging
import subprocess
import shlex
import os
import time
import sys


logging.basicConfig(
    level=logging.DEBUG,              # Set the log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S',     # Date format
)

logger = logging.getLogger(__name__)


def execute_command(command: str) -> tuple:
    """Executes a shell command and retrieves stdout, stderr, and exit code.

    :param command: The shell command to execute.
    :returns: (stdout, stderr, exit_code, command_not_found)
    """
    args = shlex.split(command)

    try:
        with subprocess.Popen(args, stdout=subprocess.PIPE,  # Capture standard output
                              stderr=subprocess.PIPE,  # Capture standard error
                              text=True) as process:
            stdout, stderr = process.communicate()  # Wait for the process to finish
            exit_code = process.returncode  # Get the exit code
            command_not_found = exit_code == 127 or "command not found" in stderr.lower()

    except FileNotFoundError as excpt:
        logger.error(f"Command \"{command}\" not found: {excpt}")
        stdout, stderr = "", "Command not found"
        exit_code = 127
        command_not_found = True

    return stdout, stderr, exit_code, command_not_found


def _assert_petalinux_is_installed():
    ''' Assert if PetaLinux tools are not installed '''
    _, _, _, not_found = execute_command('petalinux-create --help')
    if not_found:
        raise RuntimeError("Petalinux tools are not installed in this system")


class PetalinuxImageCreator:
    def __init__(self, bsp_path: str, xsa_path: str, dir: str):
        ''' Initialize petalinux image creator.

        :param bsp_path: the path to the Board Support Package file.
        :param xsa_path: the path to the XSA path to configure the PetaLinux project.
        :param dir: work directory
        '''
        self._bsp_path = bsp_path
        self._xsa_path = xsa_path
        self._dir = dir

        os.makedirs(dir, exist_ok = True)
        _assert_petalinux_is_installed()

    def _create_project(self):
        ''' Create PetaLinux project. '''
        self._proj_name = os.path.basename(os.path.splitext(self._bsp_path)[0])
        self._proj_name += f"_{int(time.time())}"
        logger.info(f"Creating PetaLinux project {self._proj_name}")
        execute_command(f'cd {self._dir} && petalinux-create -t project -s {self._bsp_path} --name {self._proj_name}')

    def _reconfigure_project_with_xsa(self):
        ''' Reconfigure PetaLinux project with .xsa file '''
        logger.info(f"Reconfiguring project {self._proj_name} with {self._xsa_path}")
        execute_command(f'cd {self._dir}/{self._proj_name} && petalinux-config --get-hw-description {self._xsa_path} --silentconfig')

    def _build(self):
        ''' Build linux images '''
        err = False
        execute_command(f'cd {self._dir}/{self._proj_name} && petalinux-build')

        for image in ("boot.scr", "image.ub"):
            image_path = f"{self._dir}/{self._proj_name}/images/linux/{image}"
            logger.info(f"Checking if {image_path} exists...")
            if os.path.isfile(image_path):
                logger.info(f"{image_path} exists!")
            else:
                logger.error(f"{image_path} does not exsists!")
                err = True

        if err:
            sys.exit(1)

    def run(self):
        ''' '''
        self._create_project()
        self._reconfigure_project_with_xsa()
def parse_args():
    """ Parse input arguments """
    parser = argparse.ArgumentParser(description="Create a Linux Image for a target board.")
    parser.add_argument('-b', '--bsp', type = str, help = "Path to board's BSP")
    parser.add_argument('-x', '--xsa', type = str, help = "Path to board's XSA")
    parser.add_argument('-d', '--dir', type = str, default = "work", help = "Work directory")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    creator = PetalinuxImageCreator(args.bsp, args.xsa, args.dir)
