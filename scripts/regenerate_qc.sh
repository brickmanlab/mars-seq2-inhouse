#!/bin/sh
#$ -N bt
#$ -S /bin/sh

if [ "$#" -ne 1 ]
then
	echo usage : regenerate_qc.sh scdb_path
	exit
fi

scdb_path=`readlink -f $1`

N_AMP_BATCHES=`tail -n +2 $scdb_path/annotations/amp_batches.txt | wc -l | cut -f 1 -d ' '`
R_HOME=`grep R_HOME $scdb_path/config/config.txt | cut -f2 -d"="`
DATA_DIR=`grep data_dir $scdb_path/config/qc_config.txt | cut -f2 -d"="`
scRNA_scripts=`grep scRNA_scripts $scdb_path/config/config.txt | cut -f2 -d"="`

qsub -wd $scdb_path -sync y -t 1-$N_AMP_BATCHES  $scRNA_scripts/distrib_qc.sh

echo "Making QC report (qc_by_batch.pdf)"
$R_HOME/Rscript $scRNA_scripts/make_qc_report.r $scdb_path $DATA_DIR

