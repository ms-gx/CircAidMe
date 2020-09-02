# How CircAidMe works

A CircAidMe run can be divided into the following high-level steps:
1. Check for every ONT read if it is a "fused read". Split any fused reads if detected.
2. Detect CircAID-p-seq adapters sequences in the (split) reads.
3. Extract inserts flanked by CircAID-p-seq adapters.
4. Perform first multiple sequence alignment (MSA) with extracted inserts from last step.
5. Remove inserts from the previous MSA which have a low quality (based on overal identity to MSA and coverage of the MSA).
6. Perform a second MSA with remaining high quality inserts.
7. Generate a consensus sequence from the second MSA.
8. Compile statistics about the CircAidMe run.

## Step 1: Split fused reads

CircAID-p-seq is based on Oxford Nanopore Technologies (ONT)-sequencing. With ONT-sequencing it can occur that the signal processing for the ONT data does not detect when a new DNA molecule goes through the pore. Meaning that two DNA molecules (reads) get fused into one read by the signal processing. We call this a "fused read".

We address this problem with two approaches:
1. Detect ONT adapters within the read (left side next figure)
2. Find a pattern of CircAID-p-seq adapters within the read which point to a fused read (right side next figure)

The detection of ONT adapters as well as detection of CircAID-p-seq adapters both get performed using [SeqAn v2.4](https://www.seqan.de/seqan-2-4-released/). If one or both of the two cases are encountered, a fused read is split at an appropriate position:

![Split reads](/aux/doc/split_reads.png)

