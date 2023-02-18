#!/usr/bin/env python
# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

__version__ = "0.0.2"


extension = [
    Pybind11Extension(
        "value_encoder",
        sources=["src/module.cpp"],
        language="c++",
        define_macros=[("VERSION_INFO", __version__)],
    )
]


setup(
    ext_modules=extension,
    cmdclass={"build_ext": build_ext},
)
