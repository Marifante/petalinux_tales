from setuptools import setup, find_packages

setup(
    name='petalinux_tales',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'petalinux_tales=petalinux_tales.cli:main',  # Adjust 'main' to the actual entry point function in cli.py
        ],
    },
    install_requires=[
        # Add your dependencies here
    ],
)
