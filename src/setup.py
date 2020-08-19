import os
from setuptools import find_namespace_packages, setup, find_packages

if os.environ.get("USE_SCM_VERSION"):
   use_scm_version = {
      "root": "..",
      "relative_to": __file__
   }
   version = None
else:
   use_scm_version = False
   version = "0.0.0"

setup(
   name='mlservicewrapper-core',
   version = version,
   use_scm_version = use_scm_version,
   description='Configure a Python service for repeated execution',
   author='Matthew Haugen',
   author_email='mhaugen@haugenapplications.com',
   #packages=find_packages(),
   packages=find_namespace_packages(include=['mlservicewrapper.*']),
   install_requires=[
      "pandas"
   ],
   #namespace_packages=['mlservicewrapper.core.errors'],
   setup_requires=['setuptools_scm'],
   zip_safe=False
)
