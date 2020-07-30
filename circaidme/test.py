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

Module for testing installation of CircAidMe
"""

# own modules
from circaidme import circaidme

# external modules
import os
import sys


def main(cli_params=None):
	
	if(cli_params==None):
		# check if path is provided and if it exists:
		if(len(sys.argv) < 2):
			sys.exit("ERROR: No output path provided. Stopping test.")
		if(not os.path.isdir(sys.argv[1])):
			sys.exit("ERROR: Provided output path does not exist. Stopping test.")
		path_test_results_folder = os.path.abspath(sys.argv[1])
	else:
		# check if path is provided and if it exists:
		if(len(cli_params) < 1):
			sys.exit("ERROR: No output path provided. Stopping test.")
		if(not os.path.isdir(cli_params[0])):
			sys.exit("ERROR: Provided output path does not exist. Stopping test.")
		path_test_results_folder = os.path.abspath(cli_params[0])

	path_test_data = os.path.dirname(os.path.abspath(__file__)) + "/test/CircAID_testdata.fastq"
	path_test_results_log = path_test_results_folder + "/CircAID_testdata.log"
	path_test_results_fasta = path_test_results_folder + "/CircAID_testdata.fasta"

	# check if output folder is empty (we do not delete anything here -- too dangerous):
	print("* Check if output path is empty ...")
	if(os.path.exists(path_test_results_fasta)): sys.exit("  ... output directory seems to be not empty. Please remove data first - ERROR")
	print("  ... done - OK")

	# run CircAidMe:	
	print("* Performing test run of CircAidMe ...")
	circaidme.main(["--input-file",path_test_data,"--out-path",path_test_results_folder,"--adapter-name","Luc20_DNA",])
	print("  ... done - OK")

	# Check if output files are there:	
	print("* Checking if output files exist ...")
	if(os.path.exists(path_test_results_log)): print("  ... logfile found - OK")
	else: sys.exit("  ... logfile not found - ERROR")
	if(os.path.exists(path_test_results_fasta)): print("  ... FASTA results found - OK")
	else: sys.exit("  ... FASTA results not found - ERROR")

	# Doing some sanity-check on logfile to see if analysis seems correct:
	print("* Doing some sanity check on logfile ...")
	with open(path_test_results_log) as f:
		if "Number of proper consensus sequences that were generated: 86" in f.read(): # this is dependent on input data, parameters and SW version
			print("  ... logfile sanity check passed - OK")
		else: sys.exit("  ... logfile sanity check NOT passed - ERROR")
