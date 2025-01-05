import argparse
import logging
import subprocess
import shlex
import os
import time
import sys
import re
import select


RED = "\033[31m"
CYAN = "\033[36m"
GREEN = "\033[92m"
YELLOW = "\033[33m"
RESET = "\033[0m"


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            record.msg = f"{GREEN}{record.msg}{RESET}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{YELLOW}{record.msg}{RESET}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{RED}{record.msg}{RESET}"

        return super().format(record)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logger level

# Create a console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # Set the handler level

# Create and set a custom formatter
formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)


def execute_command(command: str, cwd: str = "") -> tuple:
    """Executes a shell command and retrieves stdout, stderr, and exit code.

    :param command: The shell command to execute.
    :param cwd: The directory where the command will be executed. If none is given
    the same directory where the script is executed will be used.
    :returns: (stdout, stderr, exit_code, command_not_found)
    """
    stdout = ""
    stderr = ""
    process_finished = False

    args = shlex.split(command)
    logger.info(f"Executing: \"{command}\"")

    try:
        with subprocess.Popen(args, stdout=subprocess.PIPE,  # Capture standard output
                              stderr=subprocess.PIPE,  # Capture standard error
                              cwd=cwd,
                              text=True) as process:

            while not process_finished:
                reads = []

                if process.stdout:
                    reads.append(process.stdout.fileno())

                if process.stderr:
                    reads.append(process.stderr.fileno())

                ret = select.select(reads, [], [])

                for fd in ret[0]:
                    if process.stdout and fd == process.stdout.fileno():
                        stdout_line = process.stdout.readline()
                        if stdout_line:
                            print(f"{CYAN}{stdout_line}{RESET}", end='')  # Print to stdout in real-time
                            stdout += stdout_line
                    elif process.stderr and fd == process.stderr.fileno():
                        stderr_line = process.stderr.readline()
                        if stderr_line:
                            print(f"{RED}{stderr_line}{RESET}", end='', file=sys.stderr)  # Print to stderr in real-time
                            stderr += stderr_line

                # Check if the process has finished
                if process.poll() is not None:
                    process_finished = True

            exit_code = process.returncode  # Get the exit code
            command_not_found = (exit_code == 127) or ("command not found" in stderr.lower())

    except FileNotFoundError as excpt:
        logger.error(f"Command \"{command}\" not found: {excpt}")
        stdout, stderr = "", "Command not found"
        exit_code = 127
        command_not_found = True

    return stdout, stderr, exit_code, command_not_found


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


class PetalinuxCommander:
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

    def run(self):
        ''' Execute the steps of this PetaLinux commander. '''
        if 0 == len(self._steps):
            raise NotImplementedError("Steps are not defined in child class.")

        for i, step in enumerate(self._steps):
            exit_code = step()
            if 0 != exit_code:
                raise RuntimeError(f"Step {i} {step.__name__} returned exit code {exit_code}")

        logger.info("Congrats! The tool finalized correctly :)")


class PetaLinuxBSPCreator(PetalinuxCommander):
    def __init__(self, template: str, *args, **kwargs):
        ''' Initialize petalinux BSP creator.

        :param template: the template used to generate the BSP.
        '''
        self._template = template
        super().__init__(*args, **kwargs)

        # TODO: There is a bug in petalinux 2024.2 in which the project directory is 
        # not being populated during petalinux-package and it tries to use the root.
        # For that reason we are not packaging the created BSP as a BSP for now.
        # https://adaptivesupport.amd.com/s/question/0D54U00008X0fsSSAR/petalinux-20241-petalinuxpackage-fails-with-error-unable-to-create-directory-at-build?language=en_US
        self._steps = (self._create_project,
                       self._reconfigure_project_with_xsa,
                       self._wait_for_user_customization,
                       self._build,
                       self._check_post_build_images_exist,
                       self._create_boot_image_file)

    def _create_project(self) -> int:
        ''' Create empty PetaLinux project based on a template.

        :return: 0 on success, an error otherwise.
        '''
        self._proj_name = f"petalinux_tales_bsp_{self._template}"
        self._proj_name += f"_{self._petalinux_installed_version}"
        self._proj_name += f"_{int(time.time())}"

        logger.info(f"Creating PetaLinux project {self._proj_name}")
        _, _, exit_code, _ = execute_command('petalinux-create project '
                                             f'--template {self._template} '
                                             f'--name {self._proj_name}',
                                             self._dir)

        return exit_code

    def _wait_for_user_customization(self) -> int:
        ''' Let some time to the user to customize the BSP to her/his needs. '''
        logger.info(f"Now you can customize the BSP located in {self._dir}/{self._proj_name}")

        input("Press any key to continue to build")

        return 0

    def _build(self) -> int:
        ''' Build BSP.

        :return: 0 if suceed, 1 if the images are not found after creation.
        '''
        ret_val = 0
        user_finished = False

        while not user_finished:
            _, _, ret_val, _ = execute_command(f'petalinux-build', f'{self._dir}/{self._proj_name}')

            if ret_val == 0:
                user_res = input(f"{GREEN}Build succeed!{RESET} "
                                 "Do you still need to make more customizations to this BSP? "
                                 "Press Y to keep working on this and we will re-build. "
                                 "Press N if you are done with your customizations. (Y/N)")
            else:
                user_res = input(f"{RED}Build failed :({RESET} "
                                 "You can keep working in this BSP if you want. "
                                 "Press Y to keep working on this and we will re-build. "
                                 "Press N if you want to abort. (Y/N)")
                if user_res.upper() == "N":
                    ret_val = 1

            user_finished = True if user_res.upper() == 'N' else False

        return ret_val

    def _check_post_build_images_exist(self) -> int:
        ''' Check if boot.scr and image.ub exists.boot exists in the BSP.

        * boot.scr is the script read by u-boot during boot tiem to load the kernel and rootfs.
        * image.ub contains the kernel image, device tree and rootfs.

        If any of those files do not exists, the tool will fail.

        :return: 0 if succeed, otherwise an error happened.
        '''
        ret_val = 0

        for image in ("boot.scr", "image.ub"):
            image_path = f"{self._dir}/{self._proj_name}/images/linux/{image}"
            logger.info(f"Checking if {image_path} exists...")
            if os.path.isfile(image_path):
                logger.info(f"{image_path} exists!")
            else:
                logger.error(f"{image_path} does not exsists!")
                ret_val = 1

        return ret_val

    def _create_boot_image_file(self) -> int:
        ''' Create the boot image (BOOT.BIN file).

        The boot image, along with boot.scr and image.ub, is the image used to boot linux.
        It contains the:
        * FSBL (First Stage BootLoader) firmware.
        * PMU (Platform Managerment Unit) firmware.
        * TF-A (trusted Firmware with support for A-Profile ARM processors)
        * U-Boot: Second stage bootloader
        '''
        fsbl_firmware = f"{self._dir}/{self._proj_name}/images/linux/{self._template}_fsbl.elf"
        _, _, ret_val, _ = execute_command('petalinux-package boot '
                                           f'--fsbl {fsbl_firmware} --u-boot',
                                           f'{self._dir}/{self._proj_name}')

        if 0 == ret_val:
            image_path = f"{self._dir}/{self._proj_name}/images/linux/BOOT.BIN"
            if os.path.isfile(image_path):
                logger.info(f"{image_path} exists!")
            else:
                logger.error("boot image was not generated :(")
                ret_val = 1

        return ret_val


class PetalinuxImageCreator(PetalinuxCommander):
    def __init__(self, bsp_path: str, *args, **kwargs):
        ''' Initialize petalinux image creator.

        :param bsp_path: the path to the Board Support Package file.
        '''
        for file2check in (bsp_path, ):
            if not os.path.isfile(file2check):
                raise ValueError(f"{file2check} does not exists!")

        self._bsp_path = os.path.abspath(bsp_path)
        super().__init__(*args, **kwargs)

        self._steps = (self._create_project,
                       self._reconfigure_project_with_xsa,
                       self._build)

    def _create_project(self) -> int:
        ''' Create PetaLinux project.

        :return: 0 if succeed, an error otherwise.
        '''
        self._proj_name = os.path.basename(os.path.splitext(self._bsp_path)[0])
        self._proj_name += f"_{int(time.time())}"
        logger.info(f"Creating PetaLinux project {self._proj_name}")
        _, _, exit_code, _ = execute_command('petalinux-create project '
                                             f'--source {self._bsp_path} '
                                             f'--name {self._proj_name}',
                                             self._dir)

        project_path = os.path.abspath(f"{self._dir}/{self._proj_name}")

        if 0 == exit_code:
            proj_version = obtain_petalinux_project_version(project_path)
            if proj_version:
                logger.info(f"Initial version of the project = {proj_version}")
                if proj_version != self._petalinux_installed_version:
                    logger.error(f"Petalinux installed version {self._petalinux_installed_version} does not match project version {proj_version}")
                    exit_code = 2
            else:
                logger.error("Could not determine version of the created project")
                exit_code = 1

        return exit_code

    def _build(self) -> int:
        ''' Build linux images.

        :return: 0 if suceed, 1 if the images are not found after creation.
        '''
        ret_val = 0
        _, _, ret_val, _ = execute_command(f'echo "Y" | petalinux-build', f'{self._dir}/{self._proj_name}')

        if 0 == ret_val:
            for image in ("boot.scr", "image.ub"):
                image_path = f"{self._dir}/{self._proj_name}/images/linux/{image}"
                logger.info(f"Checking if {image_path} exists...")
                if os.path.isfile(image_path):
                    logger.info(f"{image_path} exists!")
                else:
                    logger.error(f"{image_path} does not exsists!")
                    ret_val = 1

        return ret_val


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
