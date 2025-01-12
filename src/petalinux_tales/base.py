import os
import re
import sys

from petalinux_tales.log import setup_logger
from petalinux_tales.utils import execute_command


logger = setup_logger(__name__)


def obtain_petalinux_project_version(project_dir: str) -> str:
    ''' Obtain the version from a created project.

    :param project_dir: the directory of the project.
    :return: a string with the version if succeed, or an empty string if fails.
    '''
    ret_val = ""
    with open(f"{project_dir}/.petalinux/metadata", 'r') as file:
        content = file.read()

    match = re.search(r'PETALINUX_VER=(\S+)', content)
    if match:
        ret_val = match.group(1)

    return ret_val


def obtain_petalinux_installed_version(install_dir: str) -> str:
    ''' Obtain petalinux installed version.

    :param install_dir: the installation dir of PetaLinux.
    :return: a string with the version if succeed, or an empty string if fails.
    '''
    ret_val = ""
    with open(f"{install_dir}/.version-history", 'r') as file:
        content = file.read()

    match = re.search(r'PETALINUX_BASE_VER=(\S+)', content)
    if match:
        ret_val = match.group(1).strip("\"")

    return ret_val


class Sequencer:
    ''' Class used to run sequences.

    The idea is to list the steps in the __init__ and then the run method
    will take care of the sequence. If a step returns 0, will follow to the next
    step. Otherwise, it will stop, returning an error.
    '''
    def __init__(self):
        ''' Constructor of sequencer base class '''
        self._steps = []

    def run(self):
        ''' Execute the steps of the sequence. '''
        if 0 == len(self._steps):
            raise NotImplementedError("Steps are not defined in child class.")

        for i, step in enumerate(self._steps):
            exit_code = step()
            if 0 != exit_code:
                raise RuntimeError(f"Step {i} {step.__name__} returned exit code {exit_code}")

        logger.info("Congrats! The tool finalized correctly :)")


class PetalinuxBase(Sequencer):
    def __init__(self, dir: str, xsa_path: str, install_dir: str):
        ''' Initialize petalinux commander.

        :param xsa_path: the path to the XSA path to configure the PetaLinux project.
        :param dir: work directory.
        :param install_dir: petalinux install dir.
        '''
        self._dir = dir

        for file2check in (xsa_path, ):
            if not os.path.isfile(file2check):
                raise ValueError(f"{file2check} does not exists!")

        self._xsa_path = os.path.abspath(xsa_path)
        self._petalinux_install_dir = os.path.abspath(install_dir)

        self._petalinux_installed_version = obtain_petalinux_installed_version(self._petalinux_install_dir)
        if self._petalinux_install_dir:
            logger.info(f"Installed PetaLinux version: {self._petalinux_installed_version}")
        else:
            logger.error("Could not determine petalinux installed version!")
            sys.exit(1)

        os.makedirs(dir, exist_ok = True)

        self._steps = tuple()
        self._proj_name = ""

    def _reconfigure_project_with_xsa(self) -> int:
        ''' Reconfigure PetaLinux project with .xsa file.

        :return: 0 if succeed, an error otherwise.
        '''
        if not self._proj_name:
            raise RuntimeError("Project name is not set, probably it was not created first.")

        logger.info(f"Reconfiguring project {self._proj_name} with {self._xsa_path}")
        _, _, exit_code, _ = execute_command(f'petalinux-config --get-hw-description {self._xsa_path} --silentconfig --debug',
                        f'{self._dir}/{self._proj_name}')

        return exit_code


