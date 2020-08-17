from setuptools import find_packages, setup

setup(
   name='mlservicewrapper',
   use_scm_version=True,
   description='Configure a Python service for repeated execution',
   author='Matthew Haugen',
   author_email='mhaugen@haugenapplications.com',
   packages=find_packages(),
   install_requires=[
      "pandas"
   ],
   setup_requires=['setuptools_scm']
)
