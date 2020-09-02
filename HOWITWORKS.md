# How CircAidMe works

A CircAidMe run can be divided into the following high-level steps:
1. Check for every ONT read if it is a "fused read". Split any fused reads if detected.
2. Detect CircAID-p-seq adapters sequences in the (split) reads & extract inserts.
3. Perform first multiple sequence alignment (MSA) with extracted inserts from last step.
4. Remove inserts from the previous MSA which have a low quality (based on overal identity to MSA and coverage of the MSA).
5. Perform a second MSA with remaining high quality inserts.
6. Generate a consensus sequence from the second MSA.
7. Compile statistics about the CircAidMe run.

## Step 1: Split fused reads

CircAID-p-seq is based on Oxford Nanopore Technologies (ONT)-sequencing. With ONT-sequencing it can occur that the signal processing for the ONT data does not detect when a new DNA molecule goes through the pore. Meaning that two DNA molecules (reads) get fused into one read by the signal processing. We call this a "fused read".

We address this problem with two approaches:
1. Detect ONT adapters within the read (left side next figure)
2. Find a pattern of CircAID-p-seq adapters within the read which point to a fused read (right side next figure)

The detection of ONT adapters as well as detection of CircAID-p-seq adapters both get performed using [SeqAn v2.4](https://www.seqan.de/seqan-2-4-released/). If one or both of the two cases are encountered, a fused read is split at an appropriate position:

![Split reads](/aux/doc/split_reads.png)

In rare cases there is more than one "fused read" event and as a result the fused read gets split up into more than one subread.

## Step 2: Detect CircAID-p-seq adapters in read & extract inserts

The split or non-split reads are now checked for CircAID-p-seq adapters using [SeqAn v2.4](https://www.seqan.de/seqan-2-4-released/).

This is the first step which will execute multicore. All the steps up to Step 6 (Generate a consensus sequence from the second MSA) are exectued on one process per read.

In order for adapter detetection to be executed a read needs a mininmal length as defined in the parameter-file of CircAidMe. If a read is too short it gets sorted out.

Inserts flanked by two CircAID-p-seq adapters are extracted:

![Extract inserts](/aux/doc/extract_insert.png)

## Step 3: Perform first multiple sequence alignment (MSA) with extracted inserts

Using [MUSCLE](https://www.drive5.com/muscle/) an MSA of the extracted inserts is calculated. However, this step is only exectued if at least two (or more, adjustable by parameter `--min-insert`) inserts are found in the previous step.

The number of iterations for the MUSCLE run can be defined via parameter `--iter-second-muscle` (default: 2, range: 1-4). However, in most cases this is an insensitive parameter and it does not change much in terms of runtime and accuracy. However, if your run takes too long you can reduce the number of iterations for this step. On the contrary, if you want a higher accuracy you can try to incrase the number of MUSCLE iterations.

## Step 4: Remove inserts from the previous MSA which have a low quality
