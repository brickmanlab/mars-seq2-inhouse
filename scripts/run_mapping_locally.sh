#!/bin/sh
#$ -S /bin/sh

if [ "$#" -ne 2 ]
then
	echo usage : run_mapping.sh scdb_path njobs
	exit
fi

scdb_path=`readlink -f $1`

FASTQ_LIST=$scdb_path/_temp/fastq_list.txt
AMP_BATCHES_TO_PROCESS=$scdb_path/config/amp_batches_to_process.txt
R_HOME=`grep R_HOME $scdb_path/config/config.txt | cut -f2 -d"="`

scRNA_scripts=`grep scRNA_scripts $scdb_path/config/config.txt | cut -f2 -d"="`

mkdir -p $scdb_path/output/
mkdir -p $scdb_path/output/QC/
mkdir -p $scdb_path/_labeled_raw_reads/
mkdir -p $scdb_path/_trimmed_mapped_reads/
mkdir -p $scdb_path/_temp
mkdir -p $scdb_path/_logs
\rm -r $scdb_path/_logs/*

annot_problems_flag=$($R_HOME/Rscript $scRNA_scripts/check_annots.r $scdb_path/)
if [ "$annot_problems_flag" != 0 ]
then
	echo ANNOTATION ERROR!!!
	cat $scdb_path/_logs/check_annots.log
	exit
fi 

fastq_problems_flag=$($R_HOME/Rscript $scRNA_scripts/create_fastq_list.r $scdb_path/ $AMP_BATCHES_TO_PROCESS $FASTQ_LIST)
if [ "$fastq_problems_flag" != 0 ]
then
	echo ANNOTATION ERROR!!!
	exit
fi 


NJOBS=`wc -l $FASTQ_LIST | cut -f 1 -d ' '`
NJOBS=`echo $NJOBS-1 | bc`
NTASKS=$NJOBS;

MAX_JOBS=$2
echo Mapping $NTASKS fastq files
touch qsub_log
i=1

while [ "$i" -le $NTASKS ]
do
   echo running $i
   $scRNA_scripts/local_mapping.sh $scdb_path $i >> $scdb_path/_logs/mapping_out.$i 2>> $scdb_path/_logs/mapping_err.$i &
  i=`echo $i+1| bc`
	sleep 1
 	running_jobs=`ps | grep local_mapping | wc -l ` 
	while [ $running_jobs -ge $MAX_JOBS ]
	do
	sleep 10
	running_jobs=`ps | grep local_mapping | wc -l `	
  done
done

while [ $running_jobs -gt 0 ]
do
	sleep 10
	running_jobs=`ps | grep local_mapping | wc -l `	
done



$R_HOME/Rscript $scRNA_scripts/check_status.r $scdb_path/ mapping $NTASKS

$R_HOME/Rscript $scRNA_scripts/merge_seq_batches_tables.r $scdb_path/
