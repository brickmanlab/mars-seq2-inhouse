#!/usr/bin/env python3
import sys
import os
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, help="Input file")
parser.add_argument("--output", type=str, help="Output file [txt separated]")
args = parser.parse_args()

if not os.path.exists(args.input):
    print('File not found')
    sys.exit()

gff = pd.read_csv(args.input, sep='\t', skiprows=7, header=None)
gff.columns = ['chrom', 'annot', 'type', 'start', 'end', 'idk', 'strand', 'idk2', 'gene_id']
gff.dropna(inplace=True)
gff = gff.query('type == "gene"')

gff.start = gff.start.astype(int)
gff.end = gff.end.astype(int)
gff.strand = gff.strand.map({'+': 1, '-': 0})

gff['gene_name'] = gff.gene_id.str.split(';', expand=True)[3].str.replace('gene_name=', '')
gff = gff[['chrom', 'start', 'end', 'strand', 'gene_name']]
gff.to_csv(args.output, index=None, sep='\t')
