#!/usr/bin/env nextflow
nextflow.enable.dsl=2

params.instring = 'Hello world!'

input_ch = Channel.fromPath('southwater_pan/contours_30130.tab')
tools_dir = /Users/oakley/Documents/GitHub/WALL-E/
analyses_dir = /Users/oakley/Documents/GitHub/WALL-E/analyses


process distance_pulses {

  input:
  file x from input_ch

  output:
  file "$x" into outputt_ch

  """
  python $tools_dir/5_find_measure_pulses/distance_pulses.py -p 
  """
}

process splitLetters {
  output:
    path 'chunk_*'

  """
  printf '${params.instring}' | split -b 6 - chunk_
  """
}

process convertToUpper {
  input:
    file x
  output:
    stdout

  """
  cat $x | tr '[a-z]' '[A-Z]'
  """
}

workflow {
  splitLetters | flatten | convertToUpper | view { it.trim() }
}
