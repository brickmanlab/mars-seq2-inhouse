#!/bin/bash

set -e

project_dir=`pwd`
reference_dir="/home/projects/dan_bri/data/DataBase/mm10-m26"

# load computerome modules
module load tools
module load bowtie2/2.3.4.1

# check if directory exists
if [ ! -d $reference_dir ]
then
    mkdir -p $reference_dir
fi

# download and extract reference
wget -O - ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M26/GRCm39.primary_assembly.genome.fa.gz | gunzip -c > $reference_dir/mm10/mm10-m26.fasta

# add ERCC into fasta
python helpers/create_ercc.py --input {{cookiecutter.project_name}}/spike-seq.txt --output $reference_dir/ercc.fasta
cat $reference_dir/ercc.fasta >> $reference_dir/mm10-m26.fasta

# extract genes and regions from gtf/gff3
wget -O - ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M26/gencode.vM26.annotation.gff3.gz | gunzip -c > $reference_dir/m10-m26.gff3
python helpers/create_annnotation.py --input $reference_dir/m10-m26.gff3 --output annotations/gene_intervals_m26.txt
cat helpers/ercc-regions.tsv >> annotations/gene_intervals_m26.txt

# build bowtie index
cd $reference_dir
bowtie2-build mm10-m26.fasta index/mm10-m26

cd $project_dir
