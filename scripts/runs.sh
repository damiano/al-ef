#!/bin/bash
CUR_DIR=`pwd`
cd `dirname $0`
#RS run
bash activelearning.sh random

#MS run
bash activelearning.sh margin

#MSD run
bash activelearning.sh margin_density density 0

#k-MSD runs
Ks="5 20 30"
for K in $Ks
do
 bash activelearning.sh margin_density k-density $K
done

#MS-RRD runs
topXs="0.025 0.05 0.2 0.3 0.5 0.7 0.9 1"
for topX in $topXs
do
  bash activelearning-reranking.sh $topX 
done
cd  $CUR_DIR

