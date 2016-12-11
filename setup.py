# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding

setup(
    name="league",
    author="Mark Christiansen",
    url="N/A",
    author_email="mark.christiansen@nuim.ie",
    version=0.1,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],
    conda_requires=["pytest", "yaml"]
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
)
