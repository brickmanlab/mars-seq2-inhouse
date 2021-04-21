#!/bin/bash

set -e

reference_dir="/home/projects/dan_bri/data/DataBase/mm10-m26"

# check if directory exists
if [ ! -d $reference_dir ]
then
    mkdir -p $reference_dir
fi

if [ ! -f $reference_dir/mm10-m26.fasta ]
then
    echo "[build_star_index.sh]> download and extract reference"
    wget -O - ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M26/GRCm39.primary_assembly.genome.fa.gz | gunzip -c > $reference_dir/mm10-m26.fasta
fi

if [ ! -f $reference_dir/m10-m26.gff3 ]
then
    echo "[build_star_index.sh]> create ERCC fasta"
    python helpers/create_ercc.py --input {{cookiecutter.project_name}}/annotations/spike-seq.txt --output $reference_dir/ercc.fasta
fi

echo "[build_star_index.sh]> build STAR index"
mkdir $reference_dir/star-index
STAR --runThreadN 30 \
    --runMode genomeGenerate \
    --genomeDir $reference_dir/star-index \
    --genomeFastaFiles $reference_dir/mm10-m26.fasta $reference_dir/ercc.fasta \
    --sjdbGTFfile $reference_dir/m10-m26.gff3 \
    --sjdbOverhang 74 # 75bp - 1

echo "[build_star_index.sh]> Done"
