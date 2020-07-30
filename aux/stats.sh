#!/bin/sh

# Copyright 2020 Michael Schmid, Genexa AG (michael.schmid@genexa.ch)
# https://github.com/ms-gx/circaidme
#
# This file is part of CircAidMe. CircAidMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version. CircAidMe is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details. You should have received a copy of the GNU General Public License along with CircAidMe. If
# not, see <http://www.gnu.org/licenses/>.

# quick hack to gather basic stats from an CircAidMe output
# needs path "stats" in same directory to work

inp_file_path=$(readlink -f $1)
inp_file_name=$(basename $inp_file_path).stats

echo "Total number of consensus seqs:" > stats/"$inp_file_name"
grep ">" $inp_file_path | wc -l >> stats/"$inp_file_name"
echo "" >> stats/"$inp_file_name"
echo "Number of variants:" >> stats/"$inp_file_name"
cat $inp_file_path | grep -v ">" | sort | uniq -c | sed 's/^ *//' | sed 's/ /\t/' | sort -k 1 -n | wc -l >> stats/"$inp_file_name"
echo "" >> stats/"$inp_file_name"
echo "Edit dist max. 3:" >> stats/"$inp_file_name"
python3 $(dirname "$0")/edit_dist.py $inp_file_path >> stats/"$inp_file_name"
echo "" >> stats/"$inp_file_name"
echo "Most:" >> stats/"$inp_file_name"
cat $inp_file_path | grep -v ">" | sort | uniq -c | sed 's/^ *//' | sed 's/ /\t/' | sort -k 1 -n | tail -n 20 >> stats/"$inp_file_name"
echo "" >> stats/"$inp_file_name"
echo "All:" >> stats/"$inp_file_name"
cat $inp_file_path | grep -v ">" | sort | uniq -c | sed 's/^ *//' | sed 's/ /\t/' | sort -k 1 -n >> stats/"$inp_file_name"

