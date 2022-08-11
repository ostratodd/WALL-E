process foo {
    output:
    val true
    script:
    """
    echo your_command_here
    """
}
process bar {
    output:
    stdout

    input:
    val ready
    path fq
    script:
    """
    echo other_commad_here --reads $fq
    """
}

workflow {
    reads_ch = Channel.fromPath("$baseDir/video_data/*.mkv")
    foo()
    bar(foo.out, reads_ch) | view
}
