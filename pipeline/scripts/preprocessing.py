#!/usr/bin/env python3
# pip install openpyxl
import sys
import glob
import logging
import argparse
import numpy as np
import pandas as pd

logging.basicConfig()
logger = logging.getLogger()
logger.propagate = False
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s  %(message)s', '%d-%m-%Y %H:%M:%S')

def read_file(folder: str, filename: str):
    file = glob.glob(f'{folder}/{filename}*.xlsx')
    if len(file) == 1:
        return pd.read_excel(file[0])
    
    logging.error(f'File {filename} coudn\'t be found!')
    sys.exit(-1)

def add_column(df, column_name, values, unique: bool = False):
    if column_name in df.columns:
        logging.warning(f'Replacing existing {column_name} with new one')

    if unique:
        df[column_name] = np.unique(values)
    else:
        df[column_name] = np.repeat(values, df.shape[0]).values if len(values) == 1 else values

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(
        description='Preprocessing script for MARS-seq2.0-inhouse pipeline'
    )

    arg_parser.add_argument('--version', '-v', action='version', version=f'v0.1')
    arg_parser.add_argument('--input', action='store', type=str, help='Input path with xls files', required=True)
    arg_parser.add_argument('--output', action='store', type=str, help='Output path to store the txt files', required=True)

    args = arg_parser.parse_args()

    # read input files from directory
    amp_batches = read_file(args.input, 'amp_batches')
    seq_batches = read_file(args.input, 'seq_batches')
    wells = read_file(args.input, 'wells_cells')

    # create amp_batches.txt
    amp_out = pd.DataFrame()
    add_column(amp_out, 'Amp_batch_ID', amp_batches['Amp_batch_ID'])
    add_column(amp_out, 'Seq_batch_ID', amp_batches['Seq_batch_ID'])
    add_column(amp_out, 'Pool_barcode', amp_batches['Pool_barcode'])
    add_column(amp_out, 'Spike_type', wells['Spike_type'])
    add_column(amp_out, 'Spike_dilution', wells['Spike_dilution'])
    add_column(amp_out, 'Spike_volume_ul', wells['Spike_volume_ul'])
    add_column(amp_out, 'Experiment_ID', amp_batches['Experiment_ID'])
    add_column(amp_out, 'Owner', amp_batches['Owner'])
    add_column(amp_out, 'Description', amp_batches['Description'])

    # create seq_batches.txt
    seq_out = pd.DataFrame()
    add_column(seq_out, 'Seq_batch_ID', amp_batches['Seq_batch_ID'], unique=True)
    add_column(seq_out, 'Run_name', seq_batches['Run_name'])
    add_column(seq_out, 'Date', seq_batches['Date'])
    add_column(seq_out, 'R1_design', seq_batches['R1_design'])
    seq_out['I5_design'] = np.NaN
    add_column(seq_out, 'R2_design', amp_batches['R2_design'])
    add_column(seq_out, 'Notes', seq_batches['Genome_assembly'])

    # wells_cells.txt
    wells_out = pd.DataFrame()
    add_column(wells_out, 'Well_ID', wells['Well_ID'])
    add_column(wells_out, 'Well_coordinates', wells['Well_coordinates'])
    add_column(wells_out, 'plate_ID', wells['plate_ID'])
    add_column(wells_out, 'Subject_ID', wells['Subject_ID'])
    add_column(wells_out, 'Amp_batch_ID', wells['Amp_batch_ID'])
    add_column(wells_out, 'Cell_barcode', wells['Cell_barcode'])
    add_column(wells_out, 'Number_of_cells', wells['Number_of_cells'])

    logging.info(f'Saving files into {args.output}...')
    amp_out.to_csv(f'{args.output}/annotations/amp_batches.txt', sep='\t', index=False)
    amp_out['Amp_batch_ID'].to_csv(f'{args.output}/config/amp_batches_to_process.txt', sep='\t', index=False)
    seq_out.to_csv(f'{args.output}/annotations/seq_batches.txt', sep='\t', index=False)
    wells_out.to_csv(f'{args.output}/annotations/wells_cells.txt', sep='\t', index=False)
