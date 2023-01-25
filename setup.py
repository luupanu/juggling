from setuptools import setup
from setuptools import Extension
import os

USE_CYTHON = False

try:
    USE_CYTHON = os.environ['USE_CYTHON']
except KeyError:
    print('Define environment variable USE_CYTHON to build from Cython source')

ext = '.pyx' if USE_CYTHON else '.c'

extensions = [
    Extension(
        'siteswap._helpers._siteswap_cython',
        ['siteswap/_helpers/_siteswap_cython' + ext]
    )
]

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)

setup(
    name='siteswap',
    version='0.1a1',
    install_requires=[
        'numpy',
        'scipy',
    ],
    ext_modules=extensions,
    packages=[
        'siteswap',
        'siteswap._helpers',
    ],
    include_package_data=True,
    zip_safe=False,
)
