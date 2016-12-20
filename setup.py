# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import find_packages, setup

setup(
    name='qiime2',
    version='2017.2.0.dev0',
    license='BSD-3-Clause',
    url='https://qiime2.org',
    packages=find_packages(),
    install_requires=['pyyaml', 'decorator', 'pandas', 'cookiecutter',
                      'tzlocal', 'python-dateutil'],
    entry_points={
        'qiime2.plugins': [
            'dummy-plugin=qiime2.core.testing.plugin:dummy_plugin'
        ]
    },
    package_data={
        'qiime2.tests': ['data/*']
    }
)
