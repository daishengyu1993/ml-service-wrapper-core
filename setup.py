import os
from setuptools import find_namespace_packages, setup, find_packages

if os.environ.get("USE_SCM_VERSION"):
   use_scm_version = True
   version = None
else:
   use_scm_version = False
   version = "0.0.0"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
   name='mlservicewrapper-core',
   version = version,
   use_scm_version = use_scm_version,
   description='Configure a Python service for repeated execution',
   author='Matthew Haugen',
   author_email='mhaugen@haugenapplications.com',

   url="https://github.com/MaJaHa95/ml-service-wrapper",
   long_description=long_description,
   long_description_content_type="text/markdown",

   package_dir={"": "src"},
   packages=find_namespace_packages("src", include=['mlservicewrapper.*']),

   install_requires=[
      "pandas"
   ],
   #namespace_packages=['mlservicewrapper.core.errors'],
   setup_requires=['setuptools_scm'],
   zip_safe=False,
   python_requires='>=3.6'
)
