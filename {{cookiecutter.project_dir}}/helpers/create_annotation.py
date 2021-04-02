#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, help="Input file [gff/gff3]")
parser.add_argument("--output", type=str, help="Output file [txt separated]")
args = parser.parse_args()

if not os.path.exists(args.input):
    print('File not found')
    sys.exit(-1)

gff = pd.read_csv(args.input, sep='\t', skiprows=7, header=None)
gff.columns = ['chrom', 'annot', 'type', 'start', 'end', 'idk', 'strand', 'idk2', 'gene_id']
gff.dropna(inplace=True)

# transcripts
gff_transcripts = gff.query('type == "transcript"')
gff_transcripts['gene_name'] = gff_transcripts.gene_id.str.split(';', expand=True)[5].str.replace('gene_name=', '')

# genes
gff_genes = gff.query('type == "gene"')
gff_genes['gene_name'] = gff_genes.gene_id.str.split(';', expand=True)[3].str.replace('gene_name=', '')

# merge both transcript and genes
gff = pd.concat([gff_transcripts, gff_genes])

# fix columns types
gff.start = gff.start.astype(int)
gff.end = gff.end.astype(int)
gff.strand = gff.strand.map({'+': 1, '-': -1})
gff = gff[['chrom', 'start', 'end', 'strand', 'gene_name']]

# save unique results
gff.drop_duplicates(inplace=True)
gff.to_csv(args.output, index=None, sep='\t')
