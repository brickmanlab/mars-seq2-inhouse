#!/bin/sh
#$ -S /bin/sh

if [ "$#" -ne 3 ]
then
	echo usage : scripts/run_mapping.sh input_dir output_dir nreads_per_file
	exit
fi


INPUT_DIR=$1
OUTPUT_DIR=$2
NREADS=$3
NLINES=`echo $NREADS*4 | bc`
for in_fn in `ls $INPUT_DIR/*.fastq.gz`; do
	echo $in_fn
	out_fn=`echo ${in_fn%.fastq.*}`
	out_fn=`echo $OUTPUT_DIR/${out_fn##*/}`
	echo "zcat $in_fn | split -l $NLINES - $out_fn"
	zcat $in_fn | split -l $NLINES - $out_fn
	for x in `ls $out_fn*`
	do
		echo mv $x $x.fastq
		mv $x $x.fastq
#		gzip $x.fastq
	done
 
done
