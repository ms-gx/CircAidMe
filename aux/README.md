# Overview auxiliary scripts

## Script to generate simple overview from CircAidMe output (stats.sh & edit_dist.py)

A simple script to generate basic statistics from the consensus Fasta output. This is neither fast nor optimized code. So running it on big Fasta file might take quite some time. `edit_dist.py` is called by `stats.sh` and they both have to be in the same directory as it is the case in this repository.

How to run:
```
mkdir stats #in the same directory as we are currently in bash
/path/to/aux/stats.sh output_circaidme.fasta
# results can be found in folder `stats`
```
