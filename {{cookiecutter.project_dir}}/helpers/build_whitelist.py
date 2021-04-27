#!/user/bin/env python3
# pip install openpyxl
import os
import glob
import argparse
import pandas as pd

if __name__ == "__main__":

    # arguments
    parser = argparse.ArgumentParser()
    # parser.add_argument("--input", type=str, help="Metadata file", required=True)
    parser.add_argument("--batch", type=str, help="Batch name", required=True)
    parser.add_argument("--input", type=str, help="Input folder with xls files", required=True)
    args = parser.parse_args()

    # metadata = pd.read_excel(args.input, index_col=0)
    # whitelist = metadata.loc[metadata['Batch'] == args.batch, ['Pool_barcode', 'Cell_barcode']].agg(''.join, axis=1).str.strip()
    # whitelist.to_csv('./whitelist.txt', header=None, index=None)

    batches = pd.read_excel(glob.glob(f'{args.input}/amp*.xlsx')[0])
    wells = pd.read_excel(glob.glob(f'{args.input}/wells*.xlsx')[0])

    batches = batches[['Seq_batch_ID', 'Pool_barcode']].sort_values(by='Seq_batch_ID')
    wells = wells[['Amp_batch_ID', 'Cell_barcode']].sort_values(by='Amp_batch_ID')

    batches = batches.astype('category')
    wells = wells.astype('category')
    
    wells['Amp_batch_ID'] = wells['Amp_batch_ID'].cat.rename_categories(batches.Pool_barcode.unique())
    wells['whitelist'] = wells[['Amp_batch_ID', 'Cell_barcode']].agg(''.join, axis=1)

    wells['whitelist'].to_csv('whitelist.txt', header=None, index=None)
