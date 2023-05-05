#!/usr/bin/env nextflow
nextflow.enable.dsl=2 

process myProcess {

    input:
    tuple val(myTuple)

    output:
    stdout

    """
    echo ${myTuple.param1}
    echo ${myTuple.param2}
    """
}

workflow {
    params.myTuple = tuple(
        param1: "value1",
        param2: "value2",
        param3: "value3",
    )
    myProcess(params.myTuple)
}

