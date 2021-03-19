#!/bin/sh
#$ -N bt
#$ -S /bin/sh

if [ "$#" -ne 2 ]
then
	echo usage : run_demultiplexing.sh scdb_path njobs
	exit
fi

scdb_path=`readlink -f $1`
AMP_BATCHES_TO_PROCESS=$scdb_path/config/amp_batches_to_process.txt
scRNA_scripts=`grep scRNA_scripts $scdb_path/config/config.txt | cut -f2 -d"="`
R_HOME=`grep R_HOME $scdb_path/config/config.txt | cut -f2 -d"="`

mkdir -p $scdb_path/_debug/
mkdir -p $scdb_path/output/
mkdir -p $scdb_path/output/QC/
mkdir -p $scdb_path/output/QC/rd/
mkdir -p $scdb_path/_temp
mkdir -p $scdb_path/_logs
rm -f $scdb_path/_logs/demultiplex*


N_AMP_BATCHES=`wc -l $AMP_BATCHES_TO_PROCESS | cut -f 1 -d ' '`
echo "Demultiplexing $N_AMP_BATCHES amplificaiton batches" ;


MAX_JOBS=$2
i=1
while [ "$i" -le $N_AMP_BATCHES ]
do
  echo running $i
  $scRNA_scripts/local_demultiplex.sh $scdb_path $i >> $scdb_path/_logs/demultiplex_out.$i 2>> $scdb_path/_logs/demultiplex_err.$i &
  i=`echo $i+1| bc`
  sleep 1
   	running_jobs=`ps | grep local_demult | wc -l ` 
  while [ $running_jobs -ge $MAX_JOBS ]
	do
	sleep 10
	running_jobs=`ps | grep local_demult | wc -l `	
  done

done

while [ $running_jobs -gt 0 ]
do
	sleep 10
	running_jobs=`ps | grep local_demult | wc -l `	
done


$R_HOME/Rscript $scRNA_scripts/check_status.r $scdb_path demultiplex $N_AMP_BATCHES
