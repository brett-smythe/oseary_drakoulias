"""Setup for oseary service"""

from setuptools import setup, find_packages
from codecs import open as cod_open
from os import path

path_to_here = path.abspath(path.dirname(__file__))


with cod_open('README.md', encoding='utf-8') as inf:
    long_description = inf.read()

reqs = []
with open('requirements.txt') as inf:
    for line in inf:
        line = line.strip()
        reqs.append(line)

setup(
    name='oseary',
    version='0.0',
    description='Scheduler for worker tasks',
    long_description=long_description,
    author='Brett Smythe',
    author_email='smythebrett@gmail.com',
    packages=find_packages(),
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'oseary-test=oseary.main:test',
            'oseary=oseary.main:run_service'
        ]
    }
)

print path_to_here
