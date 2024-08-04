#!/usr/bin/env nextflow

nextflow.enable.dsl=2

/* Downloads from Google Drive link, converts to constant frame rate (30 fps)
   and clips files according to metadata input */

/* File parameters */
params.metadata = "$baseDir/data/metadata.csv"
params.cEXT = '.mp4'
params.VIDEO_DIR='video_data'

/* Video parameters */
params.fps = 30
params.watch = 0

workflow DOWNLOAD_RAW {

    Channel.fromPath(params.metadata) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videolink, row.VL, row.VR, row.start, row.end, row.name, row.redownload, row.recfr, row.reclip) } \
        | download_videos 
        download_videos.out.vidarray | make_cfr
        make_cfr.out.vidarray | divide_smalle
}

/* COMMENTED OLD TO TEST STEP BY STEP
workflow DOWNLOAD_RAW {

    Channel.fromPath(params.metadata) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.videolink, row.VL, row.VR, row.start, row.end, row.name, row.redownload, row.recfr, row.reclip) } \
        | download_videos 
        download_videos.out.vidarray | make_cfr 
        make_cfr.out.vidarray | clip_video_pair
}

*/

workflow {
    DOWNLOAD_RAW()
}


process download_videos {

    publishDir "$params.VIDEO_DIR"

    conda = 'conda-forge::gdown'

    input:
    tuple val(videolink), val(VL), val(VR), val(start), val(end), val(name), val(redownload), val(recfr), val(reclip)

    output:
    path '*.mp4'
    tuple val(videolink), val(VL), val(VR), val(start), val(end), val(name), val(redownload), val(recfr), val(reclip), emit: vidarray

    script:
    if (redownload) {
         """
             gdown $videolink -O $name${params.cEXT}
         """
    }else{
         """
         if ls $baseDir/${params.VIDEO_DIR}/${name}${params.cEXT} 1> /dev/null 2>&1; then
             cp $baseDir/${params.VIDEO_DIR}/${name}${params.cEXT} ./
         fi
         """
    }
}

process make_cfr {
    publishDir "$params.VIDEO_DIR"

    conda = 'conda-forge::ffmpeg=4.3.1'

    input:
    tuple val(videolink), val(VL), val(VR), val(start), val(end), val(name), val(redownload), val(recfr), val(reclip)

    output:
    path '*.mp4'
    tuple val(videolink), val(VL), val(VR), val(start), val(end), val(name), val(redownload), val(recfr), val(reclip), emit: vidarray
    

    script:
    if (recfr) {
         """
         ffmpeg -i $baseDir/${params.VIDEO_DIR}/$name${params.cEXT} -f matroska -vcodec libx264 -an -framerate ${params.fps} cfr_$name${params.cEXT}
         """
    }else{
         """
         if ls $baseDir/${params.VIDEO_DIR}/cfr_$name${params.cEXT} 1> /dev/null 2>&1; then
             cp $baseDir/${params.VIDEO_DIR}/cfr_$name${params.cEXT} ./
         else
             ffmpeg -i $baseDir/${params.VIDEO_DIR}/$name${params.cEXT} -f matroska -vcodec libx264 -an -framerate ${params.fps} cfr_$name${params.cEXT}
         fi
         """
    }

}

process divide_smalle {
    publishDir "$params.VIDEO_DIR/clips"

    conda = 'conda-forge::opencv=4.5.0'

    input:
    tuple val(videolink), val(VL), val(VR), val(start), val(end), val(name), val(redownload), val(recfr), val(reclip)

    output:
    path '*.mkv'

    script:
    """
    split_smalle.py -v $baseDir/${params.VIDEO_DIR}/cfr_$name${params.cEXT} -V1 cfr_$name$VL -V2 cfr_$name$VR -s $start -e $end

    """
}

//taken from walle version
process clip_video_pair {
    publishDir "$params.VIDEO_DIR/clips"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(videolink), val(V1), val(V2), val(start), val(end), val(name), val(redownload), val(recfr), val(reclip)

    output:
    path '*.mkv'

    script: 
    if (reclip) {
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

