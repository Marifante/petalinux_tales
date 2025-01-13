#!/bin/bash

# TODO: There is a bug in petalinux 2024.2 in which the project directory is
# not being populated during petalinux-package and it tries to use the root.
# https://adaptivesupport.amd.com/s/question/0D54U00008X0fsSSAR/petalinux-20241-petalinuxpackage-fails-with-error-unable-to-create-directory-at-build?language=en_US

PETALINUX_PACKAGE_PATH=$(which petalinux-package)
BACKUP=${PETALINUX_PACKAGE_PATH}.bkp

AUTHOR_MARK="    # Fixed by petalinux-tales on "
NEW_LINES="${AUTHOR_MARK} $(date)\n"
NEW_LINES+="    if args.project:\n"
NEW_LINES+="        if isinstance(args.project, list):\n"
NEW_LINES+="            project = args.project[0]\n"
NEW_LINES+="        else:\n"
NEW_LINES+="            project = args.project\n"
NEW_LINES+="        proot = plnx_utils.exit_not_plnx_project(project)\n"
NEW_LINES+="    else:\n"
NEW_LINES+="        proot = plnx_utils.exit_not_plnx_project(proot="")\n"

if grep -q "${AUTHOR_MARK}" "${PETALINUX_PACKAGE_PATH}"; then
	echo "petalinux-package was already modified by petalinux-tales :/"
else
	echo "Modifying petalinux-package..."

	cp ${PETALINUX_PACKAGE_PATH} ${BACKUP}
	echo "Created a backup of ${PETALINUX_PACKAGE_PATH} in ${BACKUP}"

	sed -i '120,125d' ${PETALINUX_PACKAGE_PATH}
	sed -i "120a\\$NEW_LINES" ${PETALINUX_PACKAGE_PATH}
fi
