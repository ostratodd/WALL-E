process foo {
  output:
  stdout

  input:
  tuple val(sampleId), file(reads)

  script:
  """
  echo "your_command --sample $sampleId --reads $reads"
  """
}


workflow {
Channel.fromFilePairs("$baseDir/video_data/cfr_2019southwater*{L,R}.mkv", checkIfExists:true) \
    | foo

    foo.out.view()
}
