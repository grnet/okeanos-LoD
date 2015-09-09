try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Fokia',
    version='0.0.1',
    packages=['fokia'],
    url='https://github.com/grnet/okeanos-LoD',
    license='',
    author='',
    author_email='',
    description='~okeanos Lambda on Demand project',
)
