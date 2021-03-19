# In-house MARS-seq pipeline

## Building genome reference

### ERCC regions

Add ERCC into fasta file

```bash
python scripts/create_ercc.py --input references/spike-seq.txt
cat references/ercc-spikes.fasta >> /home/projects/dan_bri/scratch/MARS-seq2.0_pipeline/references/mm10-m26/GRCm39.primary_assembly.genome.fa
```

Add ERCC into annotation.

```bash
cat scdb/annotations/gene_intervals_mm9.txt | grep "ERCC" > references/ercc_regions.tsv
python references/create_annotation.py \
  --input /home/projects/dan_bri/scratch/MARS-seq2.0_pipeline/references/mm10-m26/gencode.vM26.annotation.gff3 \
  --output /home/projects/dan_bri/scratch/MARS-seq2.0_pipeline/references/mm10-m26/gene_intervals_m26.txt
cat references/ercc_regions.tsv >> /home/projects/dan_bri/scratch/MARS-seq2.0_pipeline/references/mm10-m26/gene_intervals_m26.txt 
```

### Bowtie index

```bash
cp /home/projects/dan_bri/scratch/MARS-seq2.0_pipeline/references/mm10-m26/GRCm39.primary_assembly.genome.fa /home/projects/dan_bri/scratch/MARS-seq2.0_pipeline/references/mm10-m26/mm10-m26.fa
cat references/ercc-spikes.fasta >> /home/projects/dan_bri/scratch/MARS-seq2.0_pipeline/references/mm10-m26/mm10-m26.fa
cd /home/projects/dan_bri/scratch/MARS-seq2.0_pipeline/references/mm10-m26/
bowtie2-build mm10-m26.fa mm10-m26
```

## Preprocessing

```bash
python scripts/preprocess.py --input '/path/to/xlsx' --output ./
```

## Running pipeline

```bash
module load tools
module load gcc
module load R/3.4.3
module load perl/5.24.0
module load bowtie2/2.3.4.1

scripts/split_fastqs.sh <project>/raw_reads/SB1/orig_files/ <project>/raw_reads/SB1/ 4000000
scripts/split_fastqs.sh <project>/raw_reads/SB2/orig_files/ <project>/raw_reads/SB2/ 4000000
scripts/run_pipeline_locally.sh <project>
```
