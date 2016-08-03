#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from setuptools import setup, find_packages
import os
import imp

def non_python_files(path):
    """ Return all non-python-file filenames in path """
    result = []
    all_results = []
    module_suffixes = [info[0] for info in imp.get_suffixes()]
    ignore_dirs = ['cvs']
    for item in os.listdir(path):
        name = os.path.join(path, item)
        if (
            os.path.isfile(name) and
            os.path.splitext(item)[1] not in module_suffixes
            ):
            result.append(name)
        elif os.path.isdir(name) and item.lower() not in ignore_dirs:
            all_results.extend(non_python_files(name))
    if result:
        all_results.append((path, result))
    return all_results

data_files = (
    )

setup(name='markovnet',
      version="0.0.1",
      description='Drop-in probabilistic programming.',
      author='Luke Brooks',
      author_email='luke@psybernetics.org.uk',
      url='https://github.com/LukeB42/markovnet',
      download_url = 'https://github.com/LukeB42/markovnet',
      data_files = data_files,
      packages=['markovnet'],
      include_package_data=True,
      install_requires=[],
      keywords=["probabilistic programming", "dynamic programming", "markov", "markov networks"]
)
