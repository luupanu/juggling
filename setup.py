from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

ext_modules = [
    Extension(
        name = 'siteswap.helpers._siteswap_cython',
        sources = ['siteswap/helpers/_siteswap_cython.pyx']
    )
]

setup(
    name='Siteswap generator',
    ext_modules=cythonize(ext_modules),
    zip_safe=False,
)
