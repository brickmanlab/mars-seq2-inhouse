#!/bin/bash
#$ -N scdb_rm_tmp
#$ -S /bin/bash
#$ -e /dev/null
#$ -o /dev/null

\rm /tmp/scRNA_*
