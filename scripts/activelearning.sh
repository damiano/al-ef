#!/bin/sh
sampling=$1 #random, margin, margin_density
mode=$2 #density, k-density
value=$3 #value for K parameter

CUR_DIR=`pwd`
cd `dirname $0`

if [ "$mode" == "k-density" ]
then
    K=$value
fi

NUM_THREADS=15
classifier="SVM"
representation="presence"

#set paths
stopwords="../data/stopwords"
goldstandard_training="../data/goldstandard/training/goldstandard_filtering.dat"
goldstandard_test="../data/goldstandard/test/goldstandard_filtering.dat"
training="../data/corpus/training/tweet_text/"
test="../data/corpus/test/tweet_text/"

#parameters
params="-sm $sampling -st $stopwords -g $goldstandard_training  -G $goldstandard_test   -s $training/{1}.tsv -S $test/{1}.tsv -I 1"

### define a resultsfolder and a generated/temporary folder
resultsfolder="../results"
genfolder="../gen"
run=""
if [ "$sampling" == "random" ]
then
   run="RS"

elif ["$sampling" == "margin" ]
then
   run="MS"
elif [ "$sampling" == "margin_density"]
then
    if [ "$mode" == "density" ]
    then
        run="MSD"
    elif [ "$mode" == "k-density" ]
    then
        run="k-MSD_$K"
        params="$params -K $K"
    else
      exit
    fi
else
   exit
fi
resultsfolder="$resultsfolder/$run"
genfolder="$genfolder/$run"
rm -r $resultsfolder; mkdir -p $resultsfolder
rm -r $genfolder; mkdir -p $genfolder


params="$params -o $resultsfolder/{1} -O $genfolder/{1}"

# entities="RL2013D01E001"
entities="RL2013D01E001  RL2013D01E013  RL2013D01E033 RL2013D02E054  RL2013D02E068  RL2013D03E090  RL2013D04E146  RL2013D04E161  RL2013D04E185 RL2013D01E002  RL2013D01E014  RL2013D01E035  RL2013D02E055  RL2013D02E070  RL2013D03E091  RL2013D04E149  RL2013D04E162  RL2013D04E194 RL2013D01E003  RL2013D01E015  RL2013D01E040  RL2013D02E056  RL2013D02E076  RL2013D03E093  RL2013D04E151  RL2013D04E164  RL2013D04E198 RL2013D01E005  RL2013D01E016  RL2013D01E041  RL2013D02E057  RL2013D03E086  RL2013D03E096  RL2013D04E152  RL2013D04E166  RL2013D04E206 RL2013D01E008  RL2013D01E019  RL2013D01E043  RL2013D02E060  RL2013D03E087  RL2013D03E097  RL2013D04E153  RL2013D04E167  RL2013D04E207 RL2013D01E009  RL2013D01E022  RL2013D01E044  RL2013D02E063  RL2013D03E088  RL2013D03E124  RL2013D04E155  RL2013D04E169 RL2013D01E012  RL2013D01E025  RL2013D02E051  RL2013D02E067  RL2013D03E089  RL2013D04E145  RL2013D04E159  RL2013D04E175"
parallel -P $NUM_THREADS -u --gnu python ../code/activelearning.py $params ::: $entities


#Evaluation:
iterations="0 15 30 50 100 150 300 450 600 750 900 1000 1100 1300"
for i in $iterations
do

        #Merge
        HEADER=`head -n 1 $resultsfolder/RL2013D01E001_$i`
        echo $HEADER >$resultsfolder/$i.dat

        for entity  in $entities
        do
                tail -n+2 $resultsfolder/${entity}_${i} >> $resultsfolder/$i.dat
        done
        echo  $resultsfolder/$i.dat
                # #Evaluate
                #
        perl ../scripts/EVAL_FILTERING_RS.pl $goldstandard_test $resultsfolder/$i.dat > $resultsfolder/${i}_RS.tsv
        perl ../scripts/EVAL_POLARITY_ACC.pl $goldstandard_test $resultsfolder/$i.dat > $resultsfolder/${i}_ACC.tsv
done

cd  $CUR_DIR
