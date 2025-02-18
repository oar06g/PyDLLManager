from setuptools import setup, find_packages

setup(
    name='PyDLLManager',
    version='1.2.0',
    author='Omar Mohamed',
    author_email='oar06g@gmail.com',
    description='A library for effortlessly loading DLL files in Python.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/oar06g/PyDLLManager',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
