#!/usr/bin/env python
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


extension = [
    Extension(
        "value_encoder",
        sources=[
            "src/module.cpp",
        ],
        include_dirs=[
            get_pybind_include(),
            get_pybind_include(user=True),
        ],
        language='c++'
    )
]


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""

    def build_extensions(self):
        opts = [
            '-DVERSION_INFO="%s"' % self.distribution.get_version(),
            '-std=c++14',
            '-fvisibility=hidden',
        ]
        if sys.platform == 'darwin':
            opts += ['-stdlib=libc++', '-mmacosx-version-min=10.8']

        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)


setup(
    name="value_encoder",
    version="0.0.1",
    description="Value encoder",
    author="Captricity",
    author_email="huipengh@captricity.com",
    ext_modules=extension,
    packages=['value_encoder-stubs'],
    package_data={
        'value_encoder-stubs': ['__init__.pyi'],
    },
    include_package_data=True,
    test_suite="tests",
    install_requires=['pybind11>=2.2.1'],
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
)
