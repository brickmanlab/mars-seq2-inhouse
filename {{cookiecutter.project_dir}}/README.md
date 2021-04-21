# MARS-seq2.0-inhouse template

## Create environment

```bash
module load anaconda3/4.0.0
conda env create -f environment.yml && conda clean -a
```

## Build reference

```bash
source activate mars

chmod +x ./helpers/build_reference.sh
./helpers/build_reference.sh
```

## Run pipeline

```bash
#!/bin/bash

module load tools
module load gcc
module load R/3.4.3
module load perl/5.24.0
module load anaconda3/4.0.0
module load bowtie2/2.3.4.1

# load python environment
source activate mars

# prepare files for Batch
python helpers/prepare.py --input /path/to/xlsx/folder --output {{cookiecutter.project_name}}

# split cells per Batch
scripts/split_fastqs.sh {{cookiecutter.project_name}}/raw_reads/SB1/orig_files/ {{cookiecutter.project_name}}/raw_reads/SB1/ 4000000
scripts/split_fastqs.sh {{cookiecutter.project_name}}/raw_reads/SB2/orig_files/ {{cookiecutter.project_name}}/raw_reads/SB2/ 4000000

# run pipeline
scripts/run_pipeline_locally.sh {{cookiecutter.project_name}}
```

## Run rna-velocity

```bash
#!/bin/bash

module load tools
module load openjdk/16
module load perl/5.30.2
module load fastqc/0.11.8
module load anaconda3/4.0.0
source activate mars

# build STAR index
chmod +x helpers/build_star_index.sh
./helpers/build_star_index.sh

# trim reads
module load pigz/2.3.4
module load trim_galore/0.6.4
mkdir trimmed
trim_galore --cores 10 --gzip --paired \
  {{cookiecutter.project_name}}/raw_reads/SB2/orig_files/Undetermined_S0_R1_001.fastq.gz \
  {{cookiecutter.project_name}}/raw_reads/SB2/orig_files/Undetermined_S0_R1_001.fastq.gz \
  -o trimmed | tee trimmed/trim_galore.log

# run fastqc
mkdir fastqc-trimmed
fastqc -t 2 \
  {{cookiecutter.project_name}}/raw_reads/SB2/orig_files/Undetermined_S0_R1_001.fastq.gz \
  {{cookiecutter.project_name}}/raw_reads/SB2/orig_files/Undetermined_S0_R1_001.fastq.gz \
  -o fastqc-original

# run multiqc
multiqc .

# Align with STAR
STAR --genomeDir /home/projects/dan_bri/data/DataBase/mm10-m26/star-index/ \
       --readFilesIn ../trimmed/Undetermined_S0_R1_001_val_1.fq.gz ../trimmed/Undetermined_S0_R2_001_val_2.fq.gz \
       --outSAMmultNmax 1 \
       --runThreadN 40 \
       --readNameSeparator space \
       --outSAMunmapped Within \
       --outSAMtype BAM SortedByCoordinate \
       --outFileNamePrefix SRR5945695_1 \
       --readFilesCommand gunzip -c
```

## Extra files

### `references/ercc-regions.tsv`

```bash
cat scdb/annotations/gene_intervals_mm9.txt | grep "ERCC" > references/ercc_regions.tsv
```

## Credit

_Keren-Shaul, H., Kenigsberg, E., Jaitin, D.A. et al. MARS-seq2.0: an experimental and analytical pipeline for indexed sorting combined with single-cell RNA sequencing. Nat Protoc 14, 1841–1862 (2019). https://doi.org/10.1038/s41596-019-0164-4_
