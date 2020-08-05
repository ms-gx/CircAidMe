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
"""

# own modules
from circaidme import classes
from circaidme import consensus
from circaidme import log
from circaidme import parameter
from circaidme.version import __version__

# external modules
import argparse
import multiprocessing
import os
import pathlib
import resource
from Bio import SeqIO
import shutil
import sys
import time


def main(cli_params=None): # params optional in order to enable test script to run
	# let's set up the argument parser and execute it on the input
	parser = argparse.ArgumentParser(description='CircAidMe v' + __version__ + ' -- Tool for the analysis of CircAID-p-seq data -- Designed and implemented by Genexa AG, Switzerland (genexa.ch) & Immagina BioTechnology S.R.L., Italy (immaginabiotech.com)', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser._action_groups.pop()
	required = parser.add_argument_group('required arguments')
	optional = parser.add_argument_group('optional arguments')
	required.add_argument('--input-file', dest="input_file", required=True,
			type=str,
			help='FASTA/FASTQ file with CircAID-p-seq data')
	required.add_argument('--out-path', dest="out_path", required=True,
			type=str,
			help='path to store results (also used for temp files)')
	required.add_argument('--adapter-name', dest='adapter_name', required=True,
			type=str,
			help='define which adapter to be used OR "ALL" for all the available adapters OR "LIST" if you want to provide the list of adapters to be used with argument "--adapter-list". Predefined adapters are: \"Luc20_DNA, ADR7391_RNA, ADR1_RNA, ADR2_RNA, ADR3_RNA,ADR4_RNA, ADR1572_RNA, ADR1859_RNA, ADR2520_RNA, ADR2858_RNA, ADR323_RNA, ADR4314_RNA, ADR4557_RNA, ADR4885_RNA, ADR5555_RNA\"')
	optional.add_argument('--adapter-list', dest='adapter_list',
			type=str,
			help='for user-defined adapter list (comma separated list)')
	optional.add_argument('--force-overwrite', action='store_true',
			help='set if you want to overwrite result files')
	optional.add_argument('--tag', dest='tag',
			type=str, default= "none",
			help='tag to be added to the output FASTA file')
	optional.add_argument('--refine-adapter-alignment', dest='refine_adapter',
			type=str, default="True",
			choices={"False", "True"},
			help='choose if adapter alignment has to be refined')
	optional.add_argument('--min-inserts', dest='min_inserts',
			type=int, default=parameter.min_inserts,
			help='define how many inserts have to be present in order to calculate a consensus sequence')
	optional.add_argument('--cons-min-len', dest='cons_min_len',
			type=int, default=parameter.consensus_min_len,
			help='define minimal length of the consensus sequence')
	optional.add_argument('--cons-max-len', dest='cons_max_len',
			type=int, default=parameter.consensus_max_len,
			help='define maximal length of the consensus sequence')
	optional.add_argument('--keep-forward', action='store_true',
			help='define if reads with only "forward" inserts are to be kept')
	optional.add_argument('--iter-first-muscle', dest='iter_first_muscle',
			type=int, default=2,
			choices={1,2,3},
			help='define how many iterations MUSCLE has to perform for first MSA calculation')
	optional.add_argument('--iter-second-muscle', dest='iter_second_muscle',
			type=int, default=3,
			choices={1,2,3,4},
			help='define how many iterations MUSCLE has to perform for second MSA calculation')
	optional.add_argument('--threads', dest='threads',
			type=int, default=1,
			help='number of threads to be used')
	optional.add_argument('--version', action='version', version='%(prog)s version ' + __version__)


	if(cli_params == None): args = parser.parse_args() # parse input from user
	else: args = parser.parse_args(cli_params)         # parse input provided by function call

	

	refine_adapter = True if args.refine_adapter == "True" else False
	exclude_forward = True if args.keep_forward == False else False

	# handle adapter input. We have either 1) one adapter 2) all adapters or 3) a selection of adapters defined by user
	if(args.adapter_name == "ALL"):
		adapter_names = parameter.adapter.keys()
		adapter_names = list(adapter_names)
	elif(args.adapter_name == "LIST"):
		adapter_names = args.adapter_list.replace(" ", "").split(',')
		if(not set(adapter_names).issubset(parameter.adapter)):
			print("")
			print("ERROR: User provided an unknown adapter name.")
			quit()
	else:
		adapter_names = [args.adapter_name]
		if(not set(adapter_names).issubset(parameter.adapter)):
			print("")
			print("ERROR: User provided an unknown adapter name.")
			quit()

	adapter_names.sort() # for reproducibility

	# check if output path exists
	if(not os.path.exists(args.out_path)):
		print("")
		print("ERROR: Provided output path does not exist. Please provide a valid output path. Will exit now.")
		quit()

	# little sanity check to see if we have fastx. We do just check this via file extension and not parsing the file:
	file_ending = pathlib.Path(args.input_file).suffix[1:]
	if( not ( file_ending in ["fasta","fastq"] ) ):
		print("")
		print("ERROR: Wrong file extension. Stopping analysis.")
		quit()

	# handle the tag provided by the user (if there is one)
	if(args.tag != "none"):
		tag = "_" + args.tag
	else:
		tag = ""
	file_id = pathlib.Path(args.input_file).with_suffix('').name + tag

	# clean up the output folder from temp. files before we start:
	# -> later we could define an temp folder to sepparate temp files from output...
	classes.Alignments.cleanup_all(args.out_path)

	# clean up existing output files (if they already exist only overwrite if "force-overwrite"-flag is set):
	if os.path.exists(args.out_path + "/" + file_id + ".fasta"): # contains the results
		if(args.force_overwrite == False):
			print("")
			print("ERROR: Output file already exists. If you want to overwrite please set \"force-overwrite\" flag to \"True\".")
			quit()
		os.remove(args.out_path + "/" + file_id + ".fasta")
	if os.path.exists(args.out_path + "/" + file_id + "_removed_reads.fasta"): # contains ont reads which did not result in a consensus
		os.remove(args.out_path + "/" + file_id + "_removed_reads.fasta")
	if os.path.exists(args.out_path + "/" + file_id + ".log"): # log file for an individual run
		os.remove(args.out_path + "/" + file_id + ".log")
	if os.path.exists(args.out_path + "/" + file_id + ".csv"): # statistics per read
		os.remove(args.out_path + "/" + file_id + ".csv")

	# clean up temp folder it it exists and generate it:
	if(os.path.exists(args.out_path + "/tmp_work_dir")):
		shutil.rmtree(args.out_path + "/tmp_work_dir")
	os.mkdir(args.out_path + "/tmp_work_dir")

	# init the logger
	logger = log.Log(args.out_path + "/" + file_id + ".log")

	# list to keep track of processes (workers) doing the calculations:
	procs = []
	# this we need for gracefull exit:
	flag = consensus.GracefulExiter()

	# create lock file in order to lock access to output files:
	lock = multiprocessing.Lock()

	manager = multiprocessing.Manager()
	stats = manager.dict()
	stats_per_read = manager.dict()

	stats["cnt_in_reads"] = 0
	stats["cnt_split_in_reads"] = 0
	stats["cnt_non_split_in_reads"] = 0
	stats["cnt_split_generated_reads"] = 0
	stats["cnt_proper_consensus"] = 0
	stats["fewer_two_adapters_found"] = 0
	stats["fewer_min_inserts_found"] = 0
	stats["only_forward_inserts"] = 0
	stats["problematic_insert_orientation"] = 0
	stats["bad_MSA"] = 0
	stats["adapter_as_insert"] = 0
	stats["no_minlen_subread_after_split"] = 0
	stats["consensus_size_out_of_range"] = 0
	stats["cnt_short_in_reads"] = 0

	logger.note_start()
	logger.note_command(args)

	# fetch all the ONT reads using BioPython, one by one:
	for record in SeqIO.parse(args.input_file, file_ending):

		# count the imported reads:
		with lock:
			classes.Stat.inc_key("cnt_in_reads", stats)

		waiting = True

		# now we start "args.threads" number of jobs. whenever one is done we join the process and start a new one:
		while(waiting):
			if( len(procs) < int(args.threads) ): # if we have open slots, start new processes
				# This starts the actual calculation -- one process per read:
				p = multiprocessing.Process(target=consensus.analyzeRead, args=(args.out_path, file_id, record, adapter_names, refine_adapter, exclude_forward, args.min_inserts, args.cons_min_len, args.cons_max_len, args.iter_first_muscle, args.iter_second_muscle, stats, stats_per_read, lock))
				procs.append(p) # append this process to the list holding all currently running processes
				p.start()
				waiting = False
			time.sleep(0.0001)

			for num,proc in enumerate(procs):
				if(not proc.is_alive()): # if a process is done and waiting, lets join the process and remove it from the "procs" list
					proc.join()
					procs.pop(num)
			if flag.exit(): # if user wants to exit let's do a gracefull exit. alows to clean up everything.
				break
		if flag.exit():
			break

	# wait until all remaining processes are done -- or kill them if needed (graceful exit):

	# tell proccesses to terminate -- if we stopped the analysis
	if flag.exit():
		logger.note_stop() # add a not to the logfile that user interrupted analysis run
		for proc in procs:
			if(proc.is_alive()):
				proc.terminate()

	time.sleep(0.3) # wait a bit so that the child processes of "proc" can stop... Not ideal, might be handeled with "kill()" later

	# wait until they are done
	while(len(procs) > 0):
		time.sleep(0.0001)
		for num,proc in enumerate(procs):
			if(not proc.is_alive()):
				proc.join()
				procs.pop(num)

	if(not flag.exit()):
		# calculate statistics based on "per read" information
		stats_overall_per_read = classes.Stat.print_read_stats(stats_per_read, args.out_path + "/" + file_id + ".csv")

		# write the statistics to the log file:
		classes.Stat.write_stats(stats, stats_overall_per_read, logger)

		logger.note_done()

	# do a final clean-up in the output folder:
	classes.Alignments.cleanup_all(args.out_path)

