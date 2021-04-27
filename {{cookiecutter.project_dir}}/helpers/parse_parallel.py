#!/user/bin/env python3
import os
import sys
import glob
import time
import argparse
import datetime
import textwrap
import multiprocessing as mp

from gzip import open as gzopen
from typing import Dict, List, Tuple
from Bio.SeqIO.QualityIO import FastqGeneralIterator

# MARS-seq 1
# http://dors.weizmann.ac.il/course/course2018/AnalysingRNA-SeqdataproducedbyMars-Seqprotocol.pdf
# Read #1
# @NB501779:144:HWHGFBGX9:1:11101:17900:1069 1:N:0:0
# ACAACAGAGCATATGCTGCCAGTAGCATATGCTTGTCTCAAAGATTAAGCCATGCATGTCTAAGTACGCACGGCC
# ACA       adapter (3bp)
#    ACAG   pool barcode (4bp)
#        AGCATATGCTGCCAGTAGCATATGCTTGTCTCAAAGATTAAGCCATGCATGTCTAAGTACGCACGGCC

# Read #2
# @NB501779:144:HWHGFBGX9:1:11101:17900:1069 2:N:0:0
# AAAAGAGAAAANNNN
# AAAAGAG           Cell barcode (7bp)
#        AAAANNNN   UMI (8bp)

# --------------------------------------------------------------------------------------------------

# 10X Chromium v2
# https://support.10xgenomics.com/single-cell-gene-expression/sequencing/doc/specifications-sequencing-requirements-for-single-cell-3
# Read 1 is used to sequence the 16 bp 10x Barcode and 10 bp UMI
# @NS500606:299:H2HTJBGXC:1:11101:18584:1066 1:N:0:GGTTTACT
#                                                  i7 index (8bp)
# AGGTAGGNTGAGACGTCAGATATGTC # 26 bp
# AGGTAGGNTGAGACGT           # 10x barcode (16bp)    
#                 CAGATATGTC # UMI (10bp)

# Read 2 is used to sequence the cDNA fragment.
# @NS500606:299:H2HTJBGXC:1:11101:18584:1066 2:N:0:GGTTTACT
# CTTTTTTATCCTTNNCNNANNNNNTNNTTAGNNCTTTCCNATGNANNGANNNCNCNT

# --------------------------------------------------------------------------------------------------

# Converted
# Read #1
# @NB501779:144:HWHGFBGX9:1:11101:17900:1069 1:N:0:0:GGTTTACT (i7 index) ACAGAAAAGAGAAAANNNN
# +
# /A//////E6E####

# Read #2
# @NB501779:144:HWHGFBGX9:1:11101:17900:1069 2:N:0:0:GGTTTACT (i7 index)
# AGCATATGCTGCCAGTAGCATATGCTTGTCTCAAAGATTAAGCCATGCATGTCTAAGTACGCACGGCC
# +
# EEEEEEEEEEEEEEE#EEEEEEEEEA//#/#//////////#/////////#/////#/##/#//#//

config: Dict[str, int] = {
    'LEFT_ADAPTER': 3,
    'RIGHT_ADAPTER': 2,
    'POOL_BARCODE': 4,
    'CELL_BARCODE': 7,
    'UMI': 8,
    'DEFAULT_SAMPLE_NAME': 'GGTTTACT' # arbitrary sequence
}

def mp_init(output: str):
    process.output = output

def trim_cdna(r1: List[str]) -> Tuple[str, str]:
    """Trim cdna by removing adapters and Pool barcode

    Args:
        r1 (List[str]): full cdna sequence

    Returns:
        Tuple[str, str]: trimmed cdna and quality
    """
    global config

    # [0]: header, [1]: seq, [2]: quality
    _, seq, qa = r1
    cdna: str = seq[ (config['LEFT_ADAPTER'] + config['POOL_BARCODE']) : -config['RIGHT_ADAPTER']]
    cdna_quality: str = qa[ (config['LEFT_ADAPTER'] + config['POOL_BARCODE']) : -config['RIGHT_ADAPTER']]

    return cdna, cdna_quality

def create_r2(r1: FastqGeneralIterator, r2: FastqGeneralIterator) -> Tuple[str, str]:
    """Create R2 consisting of 
        - pool barcode (4bp)
        - cell barcode (7bp)
        - UMI          (8bp)

    Args:
        r1 ([FastqGeneralIterator]): R1 read
        r2 ([FastqGeneralIterator]): R2 read

    Returns:
        Tuple[str, str]: New barcode sequence and quality
    """
    global config

    r1_head, r1_seq, r1_qa = r1
    r2_head, r2_seq, r2_qa = r2

    # get pool barcode
    pb_seq: str = r1_seq[config['LEFT_ADAPTER'] : config['LEFT_ADAPTER'] + config['POOL_BARCODE']]
    pb_qa: str = r1_qa[config['LEFT_ADAPTER'] : config['LEFT_ADAPTER'] + config['POOL_BARCODE']]

    barcode_seq: str = f'{pb_seq}{r2_seq}'
    barcode_qa: str = f'{pb_qa}{r2_qa}'

    return barcode_seq, barcode_qa

def process(fastq_files: Tuple[str, str]) -> None:
    """Main function processing the reads

    Args:
        fastq_files (Tuple[str, str]): R1, R2
    """
    fastq_r1, fastq_r2 = fastq_files

    print(f'Processing: {fastq_r1}')

    fastq_r1_out = gzopen(f'{process.output}/{os.path.basename(fastq_r1)}', "wt")
    fastq_r2_out = gzopen(f'{process.output}/{os.path.basename(fastq_r2)}', "wt")

    with gzopen(fastq_r1, "rt") as fq_r1, gzopen(fastq_r2, "rt") as fq_r2:
        
        fastq_r1 = FastqGeneralIterator(fq_r1)
        fastq_r2 = FastqGeneralIterator(fq_r2)

        for (r1, r2) in zip(fastq_r1, fastq_r2):
            # [0]: header, [1]: seq, [2]: quality
            
            cdna, cdna_quality = trim_cdna(r1)
            barcode, barcode_quality = create_r2(r1, r2)

            r1_line: str = f'''\
                @{r1[0]}:{config["DEFAULT_SAMPLE_NAME"]}
                {barcode}
                +
                {barcode_quality}
            '''

            r2_line: str = f'''\
                @{r2[0]}:{config["DEFAULT_SAMPLE_NAME"]}
                {cdna}
                +
                {cdna_quality}
            '''

            fastq_r1_out.write(textwrap.dedent(r1_line))
            fastq_r2_out.write(textwrap.dedent(r2_line))


if __name__ == "__main__":

    # arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, help="Input folder with fastq files", required=True)
    parser.add_argument("--output", type=str, help="Output folder", required=True)
    parser.add_argument("--threads", type=int, help="Number of threads", required=True, default=4)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f'The provided input folder: {args.input} doesn\'t exist!')
        sys.exit(-1)

    if not os.path.exists(args.output):
        print(f'The provided output folder: {args.output} doesn\'t exist!')
        sys.exit(-1)

    t_start = time.time()

    r1_files = sorted(glob.glob(f'{args.input}/*R1*.fastq.gz'))
    r2_files = sorted(glob.glob(f'{args.input}/*R2*.fastq.gz'))

    if len(r1_files) != len(r2_files):
        print(f'Something is off, please check you have the same amount of paired-end files!')
        sys.exit(-1)
    
    fastq_files = list(zip(r1_files, r2_files))

    with mp.Pool(args.threads, initializer=mp_init, initargs=(args.output,)) as p:
        _ = p.map(process, fastq_files)

    print(f'Done processing, took: {datetime.timedelta(seconds=(time.time() - t_start))}')
