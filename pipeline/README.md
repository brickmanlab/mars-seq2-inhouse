# In-house MARS-seq pipeline

## Run pipeline

```bash
#!/bin/bash

module load tools
module load gcc
module load R/3.4.3
module load perl/5.24.0
module load bowtie2/2.3.4.1

# prepare files for Batch
python helpers/prepare.py --input /path/to/xlsx/folder --output {{ cookiecutter.project_name }}

# split cells per Batch
scripts/split_fastqs.sh {{ cookiecutter.project_name }}/raw_reads/SB1/orig_files/ {{ cookiecutter.project_name }}/raw_reads/SB1/ 4000000
scripts/split_fastqs.sh {{ cookiecutter.project_name }}/raw_reads/SB2/orig_files/ {{ cookiecutter.project_name }}/raw_reads/SB2/ 4000000

# run pipeline
scripts/run_pipeline_locally.sh {{ cookiecutter.project_name }}
```

## Extra files

### `references/ercc-regions.tsv`

```bash
cat scdb/annotations/gene_intervals_mm9.txt | grep "ERCC" > references/ercc_regions.tsv
```
