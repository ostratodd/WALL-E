workflow {
     params.fromFile('params.yaml')
}

process foo {
    input:
    val x

    script:
    """

    echo x

    """
    
}

