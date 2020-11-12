#!/usr/bin/env python
from setuptools import setup

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext


__version__ = '0.0.1'


extension = [
    Pybind11Extension(
        "value_encoder",
        sources=[
            "src/module.cpp",
        ],
        language='c++',
        define_macros=[('VERSION_INFO', __version__)],
    )
]


setup(
    name="value_encoder",
    version=__version__,
    description="Value encoder",
    author="Hui Peng Hu",
    author_email="woohp135@gmail.com",
    ext_modules=extension,
    packages=['value_encoder-stubs'],
    package_data={
        'value_encoder-stubs': ['__init__.pyi'],
    },
    include_package_data=True,
    test_suite="tests",
    cmdclass={'build_ext': build_ext},
    zip_safe=False,
)
