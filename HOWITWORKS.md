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

The split or non-split reads are now checked for CircAID-p-seq adapters using [SeqAn v2.4](https://www.seqan.de/seqan-2-4-released/). The CircAID-p-seq adapter which has to be applied is set with parameter `--adapter-name` (required paramterer, predefined adapters see main README). In order for adapter detetection to be executed a read has to be of minimal length as defined in the parameter file of CircAidMe. If a read is too short it gets sorted out.

Mapping of the adapter to the read gets refined by adjusting the start and end of the mapping. If you suspect this to be problematic for your case you can switch this of by setting parameter `--refine-adapter-alignment` to `False`.

This is the first step which will execute multicore. All the steps up to Step 6 (Generate a consensus sequence from the second MSA) are exectued on one process per read.

Inserts flanked by two CircAID-p-seq adapters are extracted:

![Extract inserts](/aux/doc/extract_insert.png)

There are three scenarios of insert orientation that can occur: 1) forward- and reverse-inserts 2) only reverse-inserts and 3) only forward-inserts. Reads with only forward inserts get discarded by default (see publication for more information on this). If you want to keep the reads with only forward-inserts you have to set parameter ` --keep-forward`.

It can happen that a read has an insert orientation other than the three standard-cases above (for example forward-reverse-forward). A read with a non-standard orientation is excluded from the analysis.

## Step 3: Perform first multiple sequence alignment (MSA) with extracted inserts

Using [MUSCLE](https://www.drive5.com/muscle/) an MSA of the extracted inserts is calculated. However, this step is only exectued if at least two (or more, adjustable by parameter `--min-insert`) inserts are found in the previous step.

The number of iterations for the MUSCLE run can be defined via parameter `--iter-first-muscle` (default: 2, range: 1-3). However, in most cases this is an insensitive parameter and it does not change much in terms of runtime and accuracy. However, if your run takes too long you can reduce the number of iterations for this step. On the contrary, if you want a higher accuracy you can try to incrase the number of MUSCLE iterations.

## Step 4: Remove inserts with low quality from the analysis

Inserts which have a low identity to the overall MSA from the previous step or do not cover the majority of the MSA length are discarded. The thresholds for this selection process are hard-coded currently.

The following figure shows the basic idea of this step, where `Insert 3` has a bad alignment quality and `Insert 6` only covers part of the MSA:

```
Insert1  A T G T C A G C T T T G C T T A A A G T C G A T
Insert2  A T G T C A G C T T T G C T T A A A G T C G A T
Insert3  C C G   C A C C T A A G C T T T T A G A C T T T
Insert4  A T G T C A G C T T T G C A T A A A G T C G A T
Insert5  A T G A C A G C T T T G C T T A A A G T C G A T
Insert6      T G T C A G C T T T G C T T A A A
Insert7  A T G T C A G C T T T G C T T A A A G T C G A T
```

Details can be found in function `filter_good_align()` in file `classes.py`. To detect inserts with low alignment quality we use the tool [esl-alipid](https://github.com/EddyRivasLab/easel/blob/master/miniapps/esl-alipid.c).

## Step 5: Perform a second MSA with remaining high quality inserts

Using [MUSCLE](https://www.drive5.com/muscle/) an MSA of the high quality inserts is calculated.

It applies the same as for the first MSA:
The number of iterations for the second MUSCLE run can be defined via parameter `--iter-second-muscle` (default: 3, range: 1-4). However, in most cases this is an insensitive parameter and it does not change much in terms of runtime and accuracy. However, if your run takes too long you can reduce the number of iterations for this step. On the contrary, if you want a higher accuracy you can try to incrase the number of MUSCLE iterations.

## Step 6: Generate a consensus sequence from the second MSA

A custom consensus algorithm (function `cons()` in `classes.py`) is applied to the second MSA. Consensus sequences shorter than `--cons-min-len` (default: 15) and longer than `--cons-max-len` (default: 40) are discarded.

The consensus sequences are stored into *basename*.fasta.

## Step 7: Compile statistics about the CircAidMe run.

This last step compiles the statistics information and stores them into *basename*.log (overall statistics and papertrail) and *basename*.csv (statistics on a per-read level).

Reads for which no consensus sequence can be generated are stored in *basename*\_removed_reads.fasta for debugging puporse. In case you do not want to generate this file please set parameter `--no-store-removed-reads`.
