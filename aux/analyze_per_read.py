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

import sys
import regex

inserts = {
"RNA30_A":"CTATGACTTAGTTGCGTTACACCCTTTCTT",
"RNA30_G":"ACCTACCCCAGCGGCTACGAGAACCCCTTC",
"RNA30_H":"CTGTGCTCCTGTGCTACGGCCTGTGGCTGG",
"RNA30_M":"CTGAGAAAGTAGAGCAAGAAGAAATAGAGC",
"Luc20_DNA":"ATGGAAGACGCCAAAAACAT",
"ADR7391_RNA":"ACACATCGTATGCGCTGCTAGTAG",
"ADR1_RNA":"GCGCCGGGAAGAAGCACCAACCAG",
"ADR2_RNA":"GCGCCGGGTTGTTGCTCCTTCCTG",
"ADR3_RNA":"TCTCCTTTAATAATCACCAACCAT",
"ADR4_RNA":"GTGTTGGGAAGAAGTATTAATTAG",
"ADR323_RNA":"CGCGTGATACGATCTGAGACTCAT",
"ADR1572_RNA":"CGATCGACTGATGATGCACGTATC",
"ADR1859_RNA":"GCTGATCGACGATACTAGTGCTCA",
"ADR2520_RNA":"TGCTGCACATGAGTCGACTATAGC",
"ADR2858_RNA":"TGCATCATGACTCAGCGATACGTG",
"ADR4314_RNA":"TGCGACTGATAGTATCACACTGCG",
"ADR4557_RNA":"CGAGTATAGCGCAGTCTAGTCATC",
"ADR4885_RNA":"GTACGTAGACGCACTGACTGATCT",
"ADR5555_RNA":"CGCACTATCGTATCAGAGTCGTGA"
}

input_file = sys.argv[1]

with open(input_file, 'r') as in_f:
	line = in_f.readline().rstrip()
	while(line):
		if(line.startswith('>')):
			read_name = line[1:].split(" ")[0]
		else:
			multi = 0
			output = []
			for key in inserts:
				if(regex.findall("(" + line + "){e<=5}", inserts[key]) and (len(line) > 18)):
					output.append(read_name + "\t" + key + "\t" + str(multi))
					multi = multi + 1
				elif(regex.findall("(" + line + "){e<=4}", inserts[key]) and (len(line) > 15)):
					output.append(read_name + "\t" + key + "\t" + str(multi))
					multi = multi + 1
				elif(regex.findall("(" + line + "){e<=3}", inserts[key]) and (len(line) <= 15)):
					output.append(read_name + "\t" + key + "\t" + str(multi))
					multi = multi + 1
			if(len(output) == 0): # relax round one if nothing found
				for key in inserts:
					if(regex.findall("(" + line + "){e<=6}", inserts[key]) and (len(line) > 18)):
						output.append(read_name + "\t" + key + "\t" + str(multi))
						multi = multi + 1
					elif(regex.findall("(" + line + "){e<=5}", inserts[key]) and (len(line) > 15)):
						output.append(read_name + "\t" + key + "\t" + str(multi))
						multi = multi + 1
					elif(regex.findall("(" + line + "){e<=4}", inserts[key]) and (len(line) <= 15)):
						output.append(read_name + "\t" + key + "\t" + str(multi))
						multi = multi + 1
			if(len(output) == 0): # relax round two if nothing found
				for key in inserts:
					if(regex.findall("(" + line + "){e<=7}", inserts[key]) and (len(line) > 18)):
						output.append(read_name + "\t" + key + "\t" + str(multi))
						multi = multi + 1
					elif(regex.findall("(" + line + "){e<=6}", inserts[key]) and (len(line) > 15)):
						output.append(read_name + "\t" + key + "\t" + str(multi))
						multi = multi + 1
					elif(regex.findall("(" + line + "){e<=5}", inserts[key]) and (len(line) <= 15)):
						output.append(read_name + "\t" + key + "\t" + str(multi))
						multi = multi + 1
			if(len(output) == 0):
				output.append(read_name + '\t' + "none" + '\t' + '0')
			output_string = "\n".join(output)
			print(output_string)
		line = in_f.readline().rstrip()




