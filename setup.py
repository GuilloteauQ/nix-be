from setuptools import setup

setup(
    # Application name:
    name="nix-be",

    # Version number (initial):
    version="0.0.1",

    # Application author details:
    author="Quentin Guilloteau",
    author_email="Quentin.Guilloteau@univ-grenoble-alpes.fr",

    # Packages
    packages=["app"],

    # Include additional files into the package
    # include_package_data=True,
    entry_points={
        'console_scripts': ['nix-be=app.nix_be:main'],
    },

    # Details
    url="https://github.com/GuilloteauQ/nix-best-effort",

    #
    # license="LICENSE.txt",
    description="Low effort nix-shell",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
    ],
    
    include_package_data=True,
)
