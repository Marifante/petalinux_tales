import argparse
import logging
import subprocess
import shlex


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

    except FileNotFoundError:
        stdout, stderr = "", "Command not found"
        exit_code = 127
        command_not_found = True

    return stdout, stderr, exit_code, command_not_found


def _assert_petalinux_is_installed():
    ''' Assert if PetaLinux tools are not installed '''
    _, _, _, not_found = execute_command('petalinux-create')
    if not_found:
        raise RuntimeError("Petalinux tools are not installed in this system")


class PetalinuxImageCreator:
    def __init__(self, bsp_path: str):
        ''' Initialize petalinux image creator.

        :param bsp_path: the path to the Board Support Package file.
        '''
        self._bsp_path = bsp_path

        _assert_petalinux_is_installed()

    def _create_project(self):
        ''' Create PetaLinux project. '''
        execute_command(f'petalinux-create -t project -s {self._bsp_path}')


def parse_args():
    """ Parse input arguments """
    parser = argparse.ArgumentParser(description="Create a Linux Image for a target board.")
    parser.add_argument('-b', '--bsp', type = str, help = "Path to board's BSP")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    creator = PetalinuxImageCreator(args.bsp)
