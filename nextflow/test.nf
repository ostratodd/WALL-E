workflow{
params.index = "$baseDir/data/index.csv"

pairs_ch = Channel.fromPath(params.index, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.start, row.end) }

foo(pairs_ch) | bar | view
}

process bar {
    input:
        val(start)
        val(end)

    output:
        stdout

    script:
        """
        echo $start $end
        """
}

process foo {
    input:
        tuple val(start), val(end)

    output:
        val(start)
        val(end)

    script:
        """
        echo "some junk"
        """
}
