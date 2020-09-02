# How CircAidMe works

A CircAidMe run can be divided into the following high-level steps:
1. Check for every ONT read if it is a "fused read". Split any fused reads if detected.
2. Detect CircAID-p-seq adapters sequences in the (split) reads.
3. Extract inserts flanked by CircAID-p-seq adapters.
4. Perform first multiple sequenc alignment (MSA) with extracted inserts from last step.
5. Remove inserts from the previous MSA which have a low quality (based on overal identity to MSA and coverage of the MSA).
6. Perform a second MSA with remaining high quality inserts.
7. Generate a consensus sequence from the second MSA.
8. Compile statistics about the CircAidMe run.
