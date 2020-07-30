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

# this module holds the global variables and gets imported by the other modules


path_muscle = "bin/muscle"
path_esl_alipid = "bin/esl-alipid"
path_seqkit = "bin/seqkit"

ont_adapter = {
"ont_adapter_1":{"Seq":"TTGTACTTCGTTCAGTTACGTATT", "Threshold":50, "ScoringScheme":[3,-6,-5,-3]},
}

adapter = {
"Luc20_DNA":{"Seq":"ATGGAAGACGCCAAAAACAT", "Threshold":30, "ScoringScheme":[3,-6,-5,-3]},
"ADR7391_RNA":{"Seq":"ACACATCGTATGCGCTGCTAGTAG", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR1_RNA":{"Seq":"GCGCCGGGAAGAAGCACCAACCAG", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR2_RNA":{"Seq":"GCGCCGGGTTGTTGCTCCTTCCTG", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR3_RNA":{"Seq":"TCTCCTTTAATAATCACCAACCAT", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR4_RNA":{"Seq":"GTGTTGGGAAGAAGTATTAATTAG", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR323_RNA":{"Seq":"CGCGTGATACGATCTGAGACTCAT", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR1572_RNA":{"Seq":"CGATCGACTGATGATGCACGTATC", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR1859_RNA":{"Seq":"GCTGATCGACGATACTAGTGCTCA", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR2520_RNA":{"Seq":"TGCTGCACATGAGTCGACTATAGC", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR2858_RNA":{"Seq":"TGCATCATGACTCAGCGATACGTG", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR4314_RNA":{"Seq":"TGCGACTGATAGTATCACACTGCG", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR4557_RNA":{"Seq":"CGAGTATAGCGCAGTCTAGTCATC", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR4885_RNA":{"Seq":"GTACGTAGACGCACTGACTGATCT", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]},
"ADR5555_RNA":{"Seq":"CGCACTATCGTATCAGAGTCGTGA", "Threshold":40, "ScoringScheme":[3,-6,-5,-3]}
}

min_len_subread = 60

insert_min_len = 10
insert_max_len = 80

min_inserts = 2

consensus_min_len = 15
consensus_max_len = 40

