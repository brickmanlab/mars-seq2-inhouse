#!/bin/bash

set -e

reference_dir="/home/projects/dan_bri/data/DataBase/mm10-m26"

# load computerome modules
module load tools
module load bowtie2/2.3.4.1

# check if directory exists
if [ ! -d $reference_dir ]
then
    mkdir -p $reference_dir
fi

echo "[build_reference.sh]> download and extract reference"
wget -O - ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M26/GRCm39.primary_assembly.genome.fa.gz | gunzip -c > $reference_dir/mm10-m26.fasta

echo "[build_reference.sh]> add ERCC into fasta"
python helpers/create_ercc.py --input {{cookiecutter.project_name}}/annotations/spike-seq.txt --output $reference_dir/ercc.fasta

echo "[build_reference.sh]> extract genes and regions from gtf/gff3"
wget -O - ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M26/gencode.vM26.annotation.gff3.gz | gunzip -c > $reference_dir/m10-m26.gff3
python helpers/create_annotation.py --input $reference_dir/m10-m26.gff3 --output {{cookiecutter.project_name}}/annotations/gene_intervals_m26.txt
cat helpers/ercc-regions.tsv >> {{cookiecutter.project_name}}/annotations/gene_intervals_m26.txt

echo "[build_reference.sh]> build bowtie index"
mkdir $reference_dir/index
bowtie2-build $reference_dir/mm10-m26.fasta,$reference_dir/ercc.fasta $reference_dir/index/mm10-m26

echo "[build_reference.sh]> Done"
