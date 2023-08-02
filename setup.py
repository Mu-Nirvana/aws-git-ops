"""setup.py: setuptools control."""


import re
from setuptools import setup, find_packages


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('awsgitops/awsgitops.py').read(),
    re.M
    ).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "aws-gitops",
    packages = find_packages(),
    entry_points = {
        "console_scripts": ['awsgitops = awsgitops.awsgitops:main']
        },
    version = version,
    install_requires=[
        'rich',
        'click',
        'yaml',
    ],
    description = "Automatically regenerate gitops application yaml configuration files with new infrastructure data.",
    long_description_content_type='text/markdown',
    long_description = 'Checkout https://github.com/Mu-Nirvana/aws-git-ops',
    author = "Ben Campbell",
    author_email = "ben@munirvana.com",
    url = "https://github.com/Mu-Nirvana/aws-git-ops",
    )
