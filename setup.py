from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Siteswap generator',
    ext_modules=cythonize('_siteswap_cython.pyx'),
    zip_safe=False,
)
