from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in frappe_er_generator/__init__.py
from frappe_er_generator import __version__ as version

setup(
	name="frappe_er_generator",
	version=version,
	description="ERD generator for frappe doctypes",
	author="Sumit Jain",
	author_email="jainmit23@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
