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
"insert_1":"ATTCTTGTTGAATTAGATGGCGATGTTAAT",
"RNA30_G":"ACCTACCCCAGCGGCTACGAGAACCCCTTC",
"RNA30_G_rc":"GAAGGGGTTCTCGTAGCCGCTGGGGTAGGT",
"RNA30_M":"CTGAGAAAGTAGAGCAAGAAGAAATAGAGC",
"RNA30_M_rc":"GCTCTATTTCTTCTTGCTCTACTTTCTCAG",
"RNA30_A":"CTATGACTTAGTTGCGTTACACCCTTTCTT",
"RNA30_A_rc":"AAGAAAGGGTGTAACGCAACTAAGTCATAG",
"RNA30_H":"CTGTGCTCCTGTGCTACGGCCTGTGGCTGG",
"RNA30_H_rc":"CCAGCCACAGGCCGTAGCACAGGAGCACAG",
"ont_adapter_1":"TTGTACTTCGTTCAGTTACGTATT",
"Luc20_DNA":"ATGGAAGACGCCAAAAACAT",
"ADR7391_RNA":"ACACATCGTATGCGCTGCTAGTAG"
}

input_file = sys.argv[1]

for key in inserts:
	cnt_match = 0
	with open(input_file, 'r') as in_f:
		line = in_f.readline().rstrip()
		while(line):
			if(line.startswith('>')):
				pass
			elif(line != ""):
				if(regex.findall("(" + line + "){e<=3}", inserts[key]) and (len(line) > 15)):
					cnt_match = cnt_match + 1
				elif(regex.findall("(" + line + "){e<=2}", inserts[key]) and (len(line) <= 15)):
					cnt_match = cnt_match + 1
			line = in_f.readline().rstrip()
	print(key + ": " + str(cnt_match))




