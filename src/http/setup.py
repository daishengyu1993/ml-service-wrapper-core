import os
from setuptools import find_namespace_packages, setup

if os.environ.get("USE_SCM_VERSION"):
   use_scm_version = {
      "root": "../..",
      "relative_to": __file__
   }
   version = None
else:
   use_scm_version = False
   version = "0.0.0"

setup(
   name='mlservicewrapper-http',
   version = version,
   use_scm_version = use_scm_version,
   description='Configure a Python service for repeated execution',
   author='Matthew Haugen',
   author_email='mhaugen@haugenapplications.com',
   packages=find_namespace_packages(include=['mlservicewrapper.*']),
   install_requires=[
      "mlservicewrapper-core",
      "starlette==0.13.7"
   ],
   setup_requires=['setuptools_scm']
)
