from setuptools import setup, find_packages

with open("./README.md", "r") as fh:
    long_description = fh.read()
    
with open('./requirements.txt') as f:
    install_requires = [line.strip() for line in f if not line.startswith(('-','#'))]

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
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
