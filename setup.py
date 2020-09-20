#!/usr/bin/env python3
"""
Copyright 2020 Michael Schmid, Genexa AG (michael.schmid@genexa.ch)
https://github.com/ms-gx/circaidme

This file is part of CircAidMe. CircAidMe is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version. CircAidMe is distributed in
the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details. You should have received a copy of the GNU General Public License along with CircAidMe. If
not, see <http://www.gnu.org/licenses/>.

Run 'python3 setup.py build' to build CircAidMe.
Run 'python3 setup.py install' to install CircAidMe on your system.
"""

# Make sure this is being run with Python 3.5 or later (since 3.4 is end-of-life anyway).
import sys
if sys.version_info.major != 3 or sys.version_info.minor < 5:
	print('Error: you must execute setup.py using Python 3.5 or later')
	sys.exit(1)

import os
import shutil
from distutils.command.build import build
from distutils.core import Command
import subprocess
import fnmatch
import importlib.util
from setuptools import setup
from setuptools.command.install import install

# Get the program version from another file.
exec(open('circaidme/version.py').read())

#with open('README.md', 'rb') as readme:
#	LONG_DESCRIPTION = readme.read().decode()


class CircAidMeBuild(build):

	def run(self):
		build.run(self)  # Run original build code

		#clean_cmd = ['make', 'clean']
		make_cmd = ['make']

		#def clean_cpp():
		#	subprocess.call(clean_cmd)

		def compile_cpp():
			subprocess.call(make_cmd)

		#self.execute(clean_cpp, [], 'Cleaning previous compilation: ' + ' '.join(clean_cmd))
		self.execute(compile_cpp, [], 'Compiling CircAidMe: ' + ' '.join(make_cmd))


class CircAidMeInstall(install):

	def run(self):
		install.run(self)  # Run original install code


class CircAidMeClean(Command):

	user_options = []

	def initialize_options(self):
		self.cwd = None

	def finalize_options(self):
		self.cwd = os.getcwd()

	def run(self):
		assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd

		delete_directories = []
		for root, dir_names, filenames in os.walk(self.cwd):
			for dir_name in fnmatch.filter(dir_names, '*.egg-info'):
				delete_directories.append(os.path.join(root, dir_name))
			for dir_name in fnmatch.filter(dir_names, 'build'):
				delete_directories.append(os.path.join(root, dir_name))
			for dir_name in fnmatch.filter(dir_names, '__pycache__'):
				delete_directories.append(os.path.join(root, dir_name))
			for dir_name in fnmatch.filter(dir_names, 'dist'):
				delete_directories.append(os.path.join(root, dir_name))
		for delete_directory in delete_directories:
			print('Deleting directory:', delete_directory)
			shutil.rmtree(delete_directory)

		delete_files = []
		for root, dir_names, filenames in os.walk(self.cwd):
			for filename in fnmatch.filter(filenames, '*.o'):
				delete_files.append(os.path.join(root, filename))
			for filename in fnmatch.filter(filenames, '*.pyc'):
				delete_files.append(os.path.join(root, filename))
		for delete_file in delete_files:
			print('Deleting file:', delete_file)
			os.remove(delete_file)


setup(
	name='circaidme',
	version=__version__,
	description='CircAidMe',
	long_description='CircAidMe is a tool designed to analyze data generated with CircAID-p-seq (immaginabiotech.com/product/circaid-p-seq/).',
	url='https://github.com/ms-gx/CircAidMe',
	author='Michael Schmid, Ruggero Barbieri',
	author_email='michael.schmid@genexa.ch, rbarbieri@immaginabiotech.com',
	license='GPL',
	packages=['circaidme'],
	install_requires=[
		'pandas',
		'regex',
		'biopython<=1.77,>=1.73',
	],
	package_data={'circaidme': ['lib/*.so','bin/*','test/*']},
	entry_points={"console_scripts": ['circaidme = circaidme.circaidme:main','circaidme-test = circaidme.test:main']},
	zip_safe=False,
	cmdclass={
		'build': CircAidMeBuild,
		'install': CircAidMeInstall,
		'clean': CircAidMeClean,
	}
)

