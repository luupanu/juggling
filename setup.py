from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

ext_modules = [
    Extension(
        name = 'juggling.helpers._siteswap_cython',
        sources = ['juggling/helpers/_siteswap_cython.pyx']
    )
]

setup(
    name='Siteswap generator',
    ext_modules=cythonize(ext_modules),
    zip_safe=False,
)
