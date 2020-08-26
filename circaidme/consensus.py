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
from circaidme import cpp_function_wrappers
from circaidme import parameter

# external modules
from Bio.Seq import IUPAC
import math
import multiprocessing
import os
import pathlib
import regex
from Bio.Seq import Seq
import signal
import sys


# This class is needed to orchestrate the graceful exit of the multiple threads that get started for the analysis:
class GracefulExiter():
	def __init__(self):
		self.state = False
		signal.signal(signal.SIGINT, self.change_state)

	def change_state(self, signum, frame):
		print("Trying to exit gracefully ...")
		signal.signal(signal.SIGINT, signal.SIG_DFL)
		self.state = True

	def exit(self):
		return self.state


# This function detects the used adapter for multiplexed data (detects the two best hits since we might need this for fused reads)
def detect_adapter(adapters, sequence):

	if(len(adapters) == 1):
		return(adapters)

	cnt_dict = {}
	for adapter in adapters:
		alignments_adapter = (cpp_function_wrappers.adapter_alignment(sequence, parameter.adapter[adapter]["Seq"], parameter.adapter[adapter]["ScoringScheme"], parameter.adapter[adapter]["Threshold"]+12)).split("\n") # for de-multiplexing we have to increase thresholds a bit
		cnt_dict[adapter] = len(alignments_adapter[:-1])
	sorted_dict = {k: v for k, v in sorted(cnt_dict.items(), key=lambda item: item[1])}

	if( list(sorted_dict.items())[-2][1] > 1 ): return([list(sorted_dict)[-2], list(sorted_dict)[-1]]) # one other adapter has at least two hits
	else: return([list(sorted_dict)[-1]]) # only hits for one adapter


# This function detects fused ONT reads:
def detect_fused_reads(seq, adapter_names):
	cutpos = [] # to store the positions were we want to cut the read into subreads (either via identifying ONT adapter or a second change of orientation of the adapters)
	split_reason = [] # to store all the split events we encountered

	# find ONT adapters:	
	alignments_ont_adapter = (cpp_function_wrappers.adapter_alignment(seq, parameter.ont_adapter["ont_adapter_1"]["Seq"], parameter.ont_adapter["ont_adapter_1"]["ScoringScheme"], parameter.ont_adapter["ont_adapter_1"]["Threshold"])).split("\n")

	for alignment_ont in alignments_ont_adapter[:-1]:
		align_split = alignment_ont.split(";")
		cutpos.append( math.ceil( (int(align_split[2])+int(align_split[3])) / 2 ) )
		if( ( math.ceil( (int(align_split[2])+int(align_split[3])) / 2 ) > 60) and (not ("ont_adapter" in split_reason)) ):
			split_reason.append("ont_adapter")

	# perform de-multiplexing if set by user (if we have more than one adapter in list):
	if(len(adapter_names) > 1): adapter_names = detect_adapter(adapter_names, str(seq))

	# now we search for the adapters individually
	# init the read object needed for detection of second change of orientation:
	read = classes.Alignments("tmp_read", "tmp_desc", False)
	for adapter_name in adapter_names:
		# find adapters:	
		alignments_adapter = (cpp_function_wrappers.adapter_alignment(seq, parameter.adapter[adapter_name]["Seq"], parameter.adapter[adapter_name]["ScoringScheme"], parameter.adapter[adapter_name]["Threshold"]+16)).split("\n") # in current implementation, the last element in the list is an empty string // We want to increase the threshold for detecting fused reads in order to avoid false positives	

		# add alignments to the "read" object:	
		for alignment_l in alignments_adapter[:-1]:
			start_query = int(alignment_l.split(";")[2])
			end_query = int(alignment_l.split(";")[3])

			left_adjust, right_adjust = refineAlignment(seq, start_query, end_query, parameter.adapter[adapter_name]["Seq"], False) # refine the adapter alignment if necessary
		
			read.add_match(alignment_l.split(";"), left_adjust, right_adjust, adapter_name)

	read.sort() # sort the adapter alignments by coordinates
	(cut_events,type_of_cut) = read.check_fused_read() # extract the inserts and store

	if(cut_events[0] != -1):
		cutpos.extend(cut_events)
		split_reason.extend(type_of_cut)
		split_reason.sort()

	cutpos.sort() # sort the cutting positions according to index
	subreads = [] # here we store the subread sequences returned by the function
	final_adapters = [] # here we store the detected adapter for the subread

	# cut the read:	
	last_cutend = 0
	for cut in cutpos:
		sub_seq = seq[last_cutend:cut]
		if(len(sub_seq) >= parameter.min_len_subread):
			subreads.append(sub_seq)
			final_adapters.append(detect_adapter(adapter_names, str(sub_seq))[-1])
		last_cutend = cut
	sub_seq = seq[last_cutend:len(seq)]
	if(len(sub_seq) >= parameter.min_len_subread):
		subreads.append(sub_seq)
		final_adapters.append(detect_adapter(adapter_names, str(sub_seq))[-1])

	return(subreads, final_adapters, ";".join(split_reason))


# This function refines the alignment of the adapter to the ONT read:
def refineAlignment(seq, start_query, end_query, adapter_seq, print_adjustment):
	# Indices from SeqAn are zero-based and stop is non-inclusive! --> like python

	left_adjust = 0 # To store how much we want to adjust the alignment on the left side (start side)
	right_adjust = 0 # To store how much we want to adjust the alignment on the right side (start side)
	adjustment_id_left = "" # String to store what we changed on the left side. This is more for debugging purpose ...
	adjustment_id_right = "" # ... same for the right side

	# check left end of adapter:
	left_fwd_4bases = adapter_seq[0:4]; left_rev_4bases = str(Seq(adapter_seq[-4:], IUPAC.unambiguous_dna).reverse_complement())
	if((seq[start_query:end_query]).startswith(left_fwd_4bases) or (seq[start_query:end_query]).startswith(left_rev_4bases)):
		pass
	elif((seq[start_query-2:start_query+6]).find(left_fwd_4bases) != -1):
		adjustment_id_left = "AutoLeft"
		left_adjust = (seq[start_query-2:start_query+6]).find(left_fwd_4bases) - 2
	elif((seq[start_query-2:start_query+6]).find(left_rev_4bases) != -1):
		adjustment_id_left = "AutoLeft"
		left_adjust = (seq[start_query-2:start_query+6]).find(left_rev_4bases) - 2

	# check right end of adapter:
	right_fwd_4bases = adapter_seq[-4:]; right_rev_4bases = str(Seq(adapter_seq[0:4], IUPAC.unambiguous_dna).reverse_complement())
	right_fwd_8bases = adapter_seq[-8:]; right_rev_8bases = str(Seq(adapter_seq[0:8], IUPAC.unambiguous_dna).reverse_complement())
	right_fwd_last_base = adapter_seq[-1:]; right_rev_last_base = str(Seq(adapter_seq[0:1], IUPAC.unambiguous_dna).reverse_complement())
	if((seq[start_query:end_query]).endswith(right_fwd_4bases) or (seq[start_query:end_query]).endswith(right_rev_4bases)):
		pass
	elif((seq[end_query-6:end_query+2]).find(right_fwd_4bases) != -1):
		adjustment_id_right = "AutoRight1"
		right_adjust = (seq[end_query-6:end_query+2]).find(right_fwd_4bases) - 2
	elif((seq[end_query-6:end_query+2]).find(right_rev_4bases) != -1):
		adjustment_id_right = "AutoRight2"
		right_adjust = (seq[end_query-6:end_query+2]).find(right_rev_4bases) - 2
	elif(regex.findall("(" + right_fwd_8bases + "){s<=1}", seq[end_query-8:end_query+4])):
		match = regex.findall("(" + right_fwd_8bases + "){s<=1}", seq[end_query-8:end_query+4])
		if(match[0][7] == right_fwd_last_base):
			adjustment_id_right = "AutoRightDist1"
			right_adjust = (seq[end_query-8:end_query+4]).find(match[0])
	elif(regex.findall("(" + right_rev_8bases + "){s<=1}", seq[end_query-8:end_query+4])):
		match = regex.findall("(" + right_rev_8bases + "){s<=1}", seq[end_query-8:end_query+4])
		if(match[0][7] == right_rev_last_base):
			adjustment_id_right = "AutoRightDist2"
			right_adjust = (seq[end_query-8:end_query+4]).find(match[0])

	# CAUTION, print is NOT thread save. Treat output with care. This is only for testing/devel. anyway:
	if(print_adjustment == True and (adjustment_id_left != "" or adjustment_id_right != "")):
		print("Left:" + adjustment_id_left + ";" + "Right:" + adjustment_id_right)
		print("From: " + seq[start_query-16:start_query] + "*" + seq[start_query:end_query] + "*" + seq[end_query:end_query+16])
		print("To:   " + seq[start_query+left_adjust-16:start_query+left_adjust] + "*" + seq[start_query+left_adjust:end_query+right_adjust] + "*" + seq[end_query+right_adjust:end_query+right_adjust+16])
		print("")

	return (left_adjust, right_adjust)


# This function is executed for every ONT read. Every ONT read gets handeled by one thread:
def analyzeRead(outpath, file_id, record, adapter_names, refine_adapter, exclude_forward, min_inserts, cons_min_len, cons_max_len, iter_first_muscle, iter_second_muscle, stats, stats_per_read, no_store_removed_reads, lock):
	read_id = record.id
	read_desc = " ".join((record.description).split(" ")[1:])

	# check if the input read has required minimal length
	if(len(str(record.seq)) < parameter.min_len_subread):
		with lock:
			classes.Stat.inc_key("cnt_short_in_reads", stats)
			classes.Stat.init_read_stat(stats_per_read, read_id)
			classes.Stat.add_data_read_stat(stats_per_read, read_id, "len_read", len(str(record.seq)))
			classes.Stat.add_data_read_stat(stats_per_read, read_id, "final_state", "input_read_too_short")
			if(no_store_removed_reads == False):			
				with open(outpath + "/" + file_id + "_removed_reads.fasta", 'a') as out_f:
					out_f.write(">" + read_id + " inputReadTooShort" + "\n")
					out_f.write(str(record.seq) + "\n")
		return

	(subreads, adapter_names, reason_for_split) = detect_fused_reads(str(record.seq), adapter_names) # here we detect fused reads

	# count how many reads we split up:
	with lock:
		if(len(subreads) > 1):
			classes.Stat.inc_key("cnt_split_in_reads", stats)
		elif(len(subreads) == 1):
			classes.Stat.inc_key("cnt_non_split_in_reads", stats)
		elif(len(subreads) == 0):
			classes.Stat.inc_key("no_minlen_subread_after_split", stats)
			classes.Stat.inc_key("cnt_split_in_reads", stats)
			classes.Stat.init_read_stat(stats_per_read, read_id)
			classes.Stat.add_data_read_stat(stats_per_read, read_id, "len_read", len(str(record.seq)))
			classes.Stat.add_data_read_stat(stats_per_read, read_id, "final_state", "no_min_len_after_split")
			if(no_store_removed_reads == False):
				with open(outpath + "/" + file_id + "_removed_reads.fasta", 'a') as out_f:
					out_f.write(">" + read_id + " noMinLenAfterSplit" + "\n")
					out_f.write(str(record.seq) + "\n")

	for num,subread in enumerate(subreads): # read the subreads resulting from above
		adapter_name = adapter_names[num]
		if(len(subreads) > 1): # we only want to add index to read id if there is more than one subread
			read_id_sub = read_id + "-" + str(num) # add index
			# count how many subreads are generated from splits:
			with lock:
				classes.Stat.inc_key("cnt_split_generated_reads", stats)
				classes.Stat.init_read_stat(stats_per_read, read_id_sub)
				classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "adapter", adapter_name)
				classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "len_read", len(subread))
				classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "split", True)
				classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "split_reason", reason_for_split)
		else:
			read_id_sub = read_id # we do not add index
			with lock:
				classes.Stat.init_read_stat(stats_per_read, read_id_sub)
				classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "adapter", adapter_name)
				classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "len_read", len(subread))
				classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "split", False)
				classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "split_reason", "")
		
		# align with SeqAn2:
		# "seq" -> full ONT-read sequence
		alignments_adapter = (cpp_function_wrappers.adapter_alignment(subread, parameter.adapter[adapter_name]["Seq"], parameter.adapter[adapter_name]["ScoringScheme"], parameter.adapter[adapter_name]["Threshold"])).split("\n") # in current implementation, the last element in the list is an empty string
	
		with lock:
			classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "nr_adapters", len(alignments_adapter[:-1]))
		if(len(alignments_adapter[:-1]) < 2): # if we have fewer than 2 adapters detected we are not gonna use this ONT read (since we can not find an insert)
			with lock:
				classes.Stat.inc_key("fewer_two_adapters_found", stats)
				classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "final_state", "not_enough_adapters")
				if(len(alignments_adapter[:-1]) == 0):
					classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "adapter", "none")
				if(no_store_removed_reads == False):
					with open(outpath + "/" + file_id + "_removed_reads.fasta", 'a') as out_f:
						out_f.write(">" + read_id_sub + " notEnoughadapters" + "\n")
						out_f.write(subread + "\n")	
			continue

		# store adapter alignments:
		# generate the "read" object which will hold all the data for one ONT read:
		read = classes.Alignments(read_id_sub, read_desc, (len(subreads) > 1))

		# add alignments to the "read" object:	
		for alignment_l in alignments_adapter[:-1]: # add aligments to the "read" object
			start_query = int(alignment_l.split(";")[2])
			end_query = int(alignment_l.split(";")[3])

			# Here we skip the adapter refinement if desired			
			if(refine_adapter == True):			
				left_adjust, right_adjust = refineAlignment(subread, start_query, end_query, parameter.adapter[adapter_name]["Seq"], False) # refine the adapter alignment if necessary
			else:
				left_adjust, right_adjust = (0,0)

			read.add_match(alignment_l.split(";"), left_adjust, right_adjust)

		read.sort() # sort the adapter alignments by coordinates
		read.fill_inserts() # extract the inserts and store

		with lock:
			classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "nr_inserts", len(read.inserts))
	
		# here we check if we have a least "parameter.min_inserts" inserts to call a consensus:
		if( len(read.inserts) < min_inserts ):
			with lock:
				classes.Stat.inc_key("fewer_min_inserts_found", stats)
				classes.Stat.add_data_read_stat(stats_per_read, read_id_sub, "final_state", "not_enough_inserts")
				if(no_store_removed_reads == False):
					with open(outpath + "/" + file_id + "_removed_reads.fasta", 'a') as out_f:
						out_f.write(">" + read_id + " notEnoughInserts" + "\n")
						out_f.write(subread + "\n")	
			continue

		read.consensus(subread, file_id, outpath, adapter_name, exclude_forward, cons_min_len, cons_max_len, iter_first_muscle, iter_second_muscle, stats, stats_per_read, no_store_removed_reads, lock) # generate the consensus using the extracted data above. It will directly output to the resulting FASTA file.

