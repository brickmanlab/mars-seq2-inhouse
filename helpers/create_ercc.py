#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, help="Input file [annotations/spike-seq.txt]")
parser.add_argument("--output", type=str, help="Output file")
args = parser.parse_args()

if not os.path.exists(args.input):
    print('File not found')
    sys.exit(-1)

seq_length: int = 60
spikes = pd.read_csv(args.input, sep='\t')
with open(f'{args.output}/ercc.fasta', 'w') as output:
    for _, row in spikes.iterrows():
        comment = f'>{row["ERCC_ID"]}|{row["GenBank"]}|{row["5prime_assay"]}|{row["3prime_assay"]}'
        seq = '\n'.join([
            row['Sequence'][i:i+seq_length] 
            for i in range(0, len(row['Sequence']), seq_length)
            ])
        output.write(f'{comment}\n')
        output.write(f'{seq}\n')