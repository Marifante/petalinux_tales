import time
import os


from petalinux_tales.log import setup_logger, GREEN, RED, RESET
from petalinux_tales.utils import execute_command
from petalinux_tales.base import PetalinuxBase


logger = setup_logger(__name__)



class PetaLinuxBSPCreator(PetalinuxBase):
    def __init__(self, template: str, output: str, *args, **kwargs):
        ''' Initialize petalinux BSP creator.

        :param template: the template used to generate the BSP.
        :param output: path where the BSP will be stored.
        '''
        self._template = template
        super().__init__(*args, **kwargs)
        self._output = output

        # TODO: There is a bug in petalinux 2024.2 in which the project directory is
        # not being populated during petalinux-package and it tries to use the root.
        # For that reason we are not packaging the created BSP as a BSP for now.
        # https://adaptivesupport.amd.com/s/question/0D54U00008X0fsSSAR/petalinux-20241-petalinuxpackage-fails-with-error-unable-to-create-directory-at-build?language=en_US
        self._steps = (self._create_project,
                       self._reconfigure_project_with_xsa,
                       self._wait_for_user_customization,
                       self._build,
                       self._check_post_build_images_exist,
                       self._create_boot_image_file,
                       self._package_as_bsp)

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

    def _package_as_bsp(self) -> int:
        ''' Package the project as a BSP. '''
        _, _, ret_val, _ = execute_command('petalinux-package bsp '
                                           f'--project {self._dir}/{self._proj_name}'
                                           f'--output ${self._output}',
                                           f'{self._dir}/{self._proj_name}')
        return ret_val
