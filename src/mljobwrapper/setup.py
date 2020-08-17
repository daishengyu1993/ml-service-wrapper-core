from setuptools import find_packages, setup

setup(
   name='mljobwrapper',
   version='0.1',
   description='Configure a Python job for repeated execution',
   author='Matthew Haugen',
   author_email='mhaugen@haugenapplications.com',
   packages=find_packages(),
   install_requires=[
      "pandas"
   ]
)
