#!/usr/bin/env nextflow
 
params.in = "$baseDir/data/sample.fa"
 
/*
 * Split a fasta file into multiple files
 */
process splitSequences {
 
    input:
    path 'input.fa'
 
    output:
    stdout
 
    """
    echo "Yo yo ma"
    """
}
 
workflow {
    splitSequences(params.in) \
      | view
}
