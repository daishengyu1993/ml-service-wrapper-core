from setuptools import find_packages, setup

setup(
   name='jnjhttpjob',
   version='0.1',
   description='Run a jnjjobwrapper job as an HTTP service',
   author='Matthew Haugen',
   author_email='mhaugen1@its.jnj.com',
   packages=find_packages(),
   install_requires=[
      "pandas",
      "jnjjobwrapper"
   ]
)
