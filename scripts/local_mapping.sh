#!/bin/bash
#$ -N scdb_map
#$ -S /bin/bash

TASK_ID=$2
cd $1
echo `pwd`
echo $TASK_ID
R_HOME=`grep R_HOME config/config.txt | cut -f2 -d"="`
echo $R_HOME
scRNA_scripts=`grep scRNA_scripts config/config.txt | cut -f2 -d"="` 

$R_HOME/Rscript $scRNA_scripts/distrib_mapping.r $TASK_ID $scRNA_scripts _logs/mapping_status.$TASK_ID

