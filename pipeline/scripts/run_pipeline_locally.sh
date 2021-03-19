#!/bin/sh
#$ -S /bin/sh

if [ "$#" -ne 1 ]
then
	echo usage : run_pipeline_locally.sh scdb_path
	exit
fi

scdb_path=$1
number_of_cores=20

rm -f $scdb_path/_logs/mapping_status 2> /dev/null
rm -f $scdb_path/_logs/demultiplex_status 2> /dev/null

R_HOME=`grep R_HOME $scdb_path/config/config.txt | cut -f2 -d"="`
DATA_DIR=`grep data_dir $scdb_path/config/qc_config.txt | cut -f2 -d"="`
scRNA_scripts=`grep scRNA_scripts $scdb_path/config/config.txt | cut -f2 -d"="`

$scRNA_scripts/dos2unix -q annotations/*.txt 2> /dev/null
$scRNA_scripts/dos2unix -q config/amp_batces_to_process.txt 2> /dev/null

echo "--------------------------------------------------"
echo "Running mapping"
echo
$scRNA_scripts/run_mapping_locally.sh $scdb_path $number_of_cores
mapping_status=`cat $scdb_path/_logs/mapping_status`
if [[ $mapping_status != "OK" ]]
then
	exit
fi
echo
echo "--------------------------------------------------"
echo "Running demultiplex"
echo
$scRNA_scripts/run_demultiplexing_locally.sh $scdb_path $number_of_cores
demultiplex_status=`cat $scdb_path/_logs/demultiplex_status`
if [[ $demultiplex_status != "OK" ]]
then
	exit
fi
echo
echo "--------------------------------------------------"
echo "Merging QC reports"
$R_HOME/Rscript $scRNA_scripts/make_qc_report.r $scdb_path $DATA_DIR > $scdb_path/_logs/make_qc_report.log  2> $scdb_path/_logs/make_qc_report.log

echo
echo "--------------------------------------------------"
echo "Done"
