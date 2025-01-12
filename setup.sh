#!/bin/bash

VENV_NAME="petalinux-tales-venv"

rm -rf ${VENV_NAME} >/dev/null 2>&1

python3 -m venv ${VENV_NAME}

source ${VENV_NAME}/bin/activate

echo "Virtual environment activated"

pip install -e .
