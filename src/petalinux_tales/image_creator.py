import os
import time

from petalinux_tales.log import setup_logger
from petalinux_tales.utils import execute_command
from petalinux_tales.base import PetalinuxBase, obtain_petalinux_project_version


logger = setup_logger(__name__)


class PetalinuxImageCreator(PetalinuxBase):
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

