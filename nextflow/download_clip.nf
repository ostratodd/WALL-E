#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
   and clips files according to metadata input */

params.redownload = true
params.recfr = true
params.reclip = true

/* File parameters */
params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'

/* Video parameters */
params.fps = 30
params.watch = 0

workflow DOWNLOAD_RAW {

    Channel.fromPath(params.metadata) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.VL, row.linkL, row.VR, row.linkR, row.start, row.end, row.offset, row.name) } \
        | download_videos 
        download_videos.out.vidarray | make_cfr 
        make_cfr.out.vidarray | clip_video_pair
}

workflow {
    DOWNLOAD_RAW()
}


process clip_video_pair {
    publishDir "$params.VIDEO_DIR/clips"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(V1), val(V2), val(start), val(end), val(offset), val(name)

    output:
    path '*.mkv'

    script:

    script: 
    if (params.reclip) {
         """
         clip2vids.py -v1 $baseDir/${params.VIDEO_DIR}/cfr_$name$V1${params.cEXT} -v2 $baseDir/${params.VIDEO_DIR}/cfr_$name$V2${params.cEXT} -s $start -e $end -o $offset -w ${params.watch}
         """
    }else{
         """
         if ls $baseDir/${params.VIDEO_DIR}/clips/${name}${V1}_cl_${start}_${end}_undis.mkv 1> /dev/null 2>&1; then
             cp $baseDir/${params.VIDEO_DIR}/clips/${name}${V1}_cl_${start}_${end}_undis.mkv ./
             cp $baseDir/${params.VIDEO_DIR}/clips/${name}${V2}_cl_${start}_${end}_undis.mkv ./
         else
             clip2vids.py -v1 $baseDir/${params.VIDEO_DIR}/cfr_$name$V1${params.cEXT} -v2 $baseDir/${params.VIDEO_DIR}/cfr_$name$V2${params.cEXT} -s $start -e $end -o $offset -w ${params.watch}
         fi
         """
    }
}

process download_videos {

    publishDir "$params.VIDEO_DIR"

    conda = 'conda-forge::gdown'

    input:
    tuple val(videoL), val(linkL), val(videoR), val(linkR), val(start), val(end), val(offset), val(name)

    output:
    path '*.mkv'
    tuple val(videoL), val(videoR), val(start), val(end), val(offset), val(name), emit: vidarray

    script:
    if (params.redownload) {
         """
             gdown $linkL -O $name$videoL${params.cEXT}
             gdown $linkR -O $name$videoR${params.cEXT}
         """
    }else{
         """
         if ls $baseDir/${params.VIDEO_DIR}/${name}${videoL}${params.cEXT} 1> /dev/null 2>&1; then
             cp $baseDir/${params.VIDEO_DIR}/${name}${videoL}${params.cEXT} ./
             cp $baseDir/${params.VIDEO_DIR}/${name}${videoR}${params.cEXT} ./
         fi
         """
    }
}
process make_cfr {
    publishDir "$params.VIDEO_DIR"

    conda = 'conda-forge::ffmpeg=4.3.1'

    input:
    tuple val(V1), val(V2), val(start), val(end), val(offset), val(name)

    output:
    path '*.mkv'
    tuple val(V1), val(V2), val(start), val(end), val(offset), val(name), emit: vidarray
    

    script:
    if (params.recfr) {
         """
         ffmpeg -i $baseDir/${params.VIDEO_DIR}/$name$V1${params.cEXT} -f matroska -vcodec libx264 -an -framerate ${params.fps} cfr_$name$V1${params.cEXT}
         ffmpeg -i $baseDir/${params.VIDEO_DIR}/$name$V2${params.cEXT} -f matroska -vcodec libx264 -an -framerate ${params.fps} cfr_$name$V2${params.cEXT}
         """
    }else{
         """
         if ls $baseDir/${params.VIDEO_DIR}/cfr_$name$V1${params.cEXT} 1> /dev/null 2>&1; then
             cp $baseDir/${params.VIDEO_DIR}/cfr_$name$V1${params.cEXT} ./
             cp $baseDir/${params.VIDEO_DIR}/cfr_$name$V2${params.cEXT} ./
         else
             ffmpeg -i $baseDir/${params.VIDEO_DIR}/$name$V1${params.cEXT} -f matroska -vcodec libx264 -an -framerate ${params.fps} cfr_$name$V1${params.cEXT}
             ffmpeg -i $baseDir/${params.VIDEO_DIR}/$name$V2${params.cEXT} -f matroska -vcodec libx264 -an -framerate ${params.fps} cfr_$name$V2${params.cEXT}
         fi
         """
    }

}

