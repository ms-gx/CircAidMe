# Overview auxiliary material

## Folder `fasta`

Fasta files containing the CircAID-p-seq adapters as well as the inserts used for the publication.

## Statistics script to generate simple overview from CircAidMe output (`stats.sh` & `edit_dist.py`)

A simple script to generate basic statistics from the consensus Fasta output. It will print some basic statistics, will identify some known CircAidMe inserts and will plot the most common variants of the consensus it found.

This is neither fast nor optimized code. So running it on big Fasta file might take quite some time. `edit_dist.py` is called by `stats.sh` and they both have to be in the same directory as it is the case in this repository.

How to run:
```
mkdir stats #in the same directory as we are currently in bash
/path/to/aux/stats.sh output_circaidme.fasta
# results can be found in folder `stats`
```

## Asignment of consensus seaquence per read (`analyze_per_read.py`)

This script will asign every consensus sequence of the consensus Fasta file to an insert sequence contained in the python script. If it can be found in the candidate insert sequences obviously. Otherwise it will report `none`.

How to run:
```
python3 /path/to/analyze_per_read.py output_circaidme.fasta > results.txt
```

## Script for quantification of "pool" data of publication (`quant_insert_pool_data.py`)

This script was used to quantify the results from the "pool" analysis of CircAID-p-seq publication.

How to run:
```
#PoolA:
python3 /path/to/quant_insert_pool.py output_pooldataA_circaidme.fasta > poolA_inserts.txt
awk '$3==0' poolA_inserts.txt | cut -f 2 | sort | uniq -c > poolA_count.txt
#PoolB:
python3 /path/to/quant_insert_pool.py output_pooldataB_circaidme.fasta > poolB_inserts.txt
awk '$3==0' poolB_inserts.txt | cut -f 2 | sort | uniq -c > poolB_count.txt
```
