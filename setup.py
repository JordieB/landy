import os
from setuptools import setup, find_packages

# get the path of setup.py file
here = os.path.abspath(os.path.dirname(__file__))
readme_fp = os.path.join(here, 'README.md')

with open(readme_fp, "r") as fh:
    long_description = fh.read()

setup(
    name='Landy',
    version='0.1',
    description='A Discord bot for Dungeon Fighter Online Global questions',
    author='Jordie Belle',
    author_email='jordie.belle@proton.me',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/JordieB/landy',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
