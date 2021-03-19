#!/bin/bash
#$ -N scdb_qc
#$ -S /bin/bash
#$ -e _logs/demultiplex_err.$TASK_ID
#$ -o _logs/demultiplex.$TASK_ID


AMP_BATCH_ID=`cut -f1 annotations/amp_batches.txt | tail -n +2 | head -n $SGE_TASK_ID | tail -n 1`
R_HOME=`grep R_HOME config/config.txt | cut -f2 -d"="`
DATA_DIR=`grep data_dir config/qc_config.txt | cut -f2 -d"="`
scRNA_scripts=`grep scRNA_scripts config/config.txt | cut -f2 -d"="`

echo qc amplification batch $AMP_BATCH_ID
$R_HOME/Rscript $scRNA_scripts/make_batch_qc.r $AMP_BATCH_ID $DATA_DIR
