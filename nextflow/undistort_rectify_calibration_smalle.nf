#!/usr/bin/env nextflow

nextflow.enable.dsl=2

mode = "internal" 		/* internal mode collects frame images from video */
/* mode = "external"*/


params.cEXT = '.mkv'
params.VIDEO_DIR='video_data'
params.DATA_DIR='data'

params.watchvideo = 0

/*Must include config file with parameters */

workflow MAKE_STEREO_MAPS {
    stereo_ch = Channel.fromPath(params.metadata, checkIfExists:true) \
        | splitCsv(header:true) \
        | map { row-> tuple(row.name, row.VL, row.VR, row.start, row.end, row.offset) }

    find_all_singles(stereo_ch)
    find_all_singles.out | select_frames
    select_frames.out.vidarray | find_all_pairs
    find_all_pairs.out | select_pairs
    select_pairs.out | new_calibrate
    new_calibrate.out.vidarray | new_rectify
}

workflow {
    MAKE_STEREO_MAPS()
}

process find_all_singles {
    publishDir "$params.VIDEO_DIR/data"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset)

    output:
    path '*.csv'
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), emit: vidarray

    script:
    if (params.reid_frames) {
         """
         if ls $baseDir/${params.VIDEO_DIR}/data/${name}_frames_L.csv 1> /dev/null 2>&1; then
             rm $baseDir/${params.VIDEO_DIR}/data/${name}_frames_L.csv
         fi
         if ls $baseDir/${params.VIDEO_DIR}/data/${name}_frames_R.csv 1> /dev/null 2>&1; then
             rm $baseDir/${params.VIDEO_DIR}/data/${name}_frames_R.csv
         fi
         id_all_checkerframes.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}.mkv -o ${name}_frames_R.csv -c ${params.checkdim} -l ${params.watchvideo}
         id_all_checkerframes.py -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}.mkv -o ${name}_frames_L.csv -c ${params.checkdim} -l ${params.watchvideo}

         """
    }else{
         """
         echo "MESSAGE: Using existing csv file containing frame numbers with checkerboards for individual frames because reid_frames=0 in config file"
         cp $baseDir/${params.VIDEO_DIR}/data/${name}_frames_L.csv ./
         cp $baseDir/${params.VIDEO_DIR}/data/${name}_frames_R.csv ./
         """
    }
}

process select_frames {
    publishDir "$params.VIDEO_DIR/pairs"

    conda = 'conda-forge::matplotlib=3.3.3 conda-forge::pandas=1.2.0  conda-forge::opencv=4.5.0  conda-forge::numpy=1.19.4'

    input:
    path csvfiles
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset)

    output:
    file '*.png'
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), emit: vidarray

   script:
    if (params.refind_frames) {
         """
#*****NEED TO CHECK IF THESE FILES EXIST AND IF SO TO DELETE, BUT IF NOT TO SKIP THIS STEP, OTHERWISE IT WILL CRASH
         rm $baseDir/${params.VIDEO_DIR}/pairs/${name}_L_single*.png
         rm $baseDir/${params.VIDEO_DIR}/pairs/${name}_R_single*.png
         select_frames.py -p ${name}_L -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}.mkv -f $baseDir/${params.VIDEO_DIR}/data/${name}_frames_L.csv -e ${params.L_dist} -n ${params.L_n} -l ${params.watchvideo}
         select_frames.py -p ${name}_R -v $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}.mkv -f $baseDir/${params.VIDEO_DIR}/data/${name}_frames_R.csv -e ${params.R_dist} -n ${params.R_n} -l ${params.watchvideo}
         """
    }else{
         """
         echo "MESSAGE: Used the same  paired checkerboard frame images (png)  because reid_pairs = 1 in params file"
         cp $baseDir/${params.VIDEO_DIR}/pairs/${name}_L_single*.png ./
         cp $baseDir/${params.VIDEO_DIR}/pairs/${name}_R_single*.png ./
         """
    }
}

process find_all_pairs {
    publishDir "$params.VIDEO_DIR/data"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset)

    output:
    path '*.csv'
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), emit: vidarray

    script:

    if (params.reid_pairs) {
         """
         if ls $baseDir/${params.VIDEO_DIR}/data/${name}_pairs.csv 1> /dev/null 2>&1; then
             rm $baseDir/${params.VIDEO_DIR}/data/${name}_pairs.csv
         fi
         id_all_pairs.py -v1 $baseDir/${params.VIDEO_DIR}/clips/${name}${VR}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/${name}${VL}_cl_${start}_${end}_undis.mkv -o ${name}_pairs.csv -c ${params.checkdim} -l ${params.watchvideo}

         """
    }else{
         """
         cp $baseDir/${params.VIDEO_DIR}/data/${name}_pairs.csv ./
         echo "MESSAGE: Used existing csv file containing frame numbers with paired checkerboards because reid_pairs = 1 in params file"
         """
    }
}

process select_pairs {
    publishDir "$params.VIDEO_DIR/pairs"

    conda = 'conda-forge::matplotlib=3.3.3 conda-forge::pandas=1.2.0  conda-forge::opencv=4.5.0  conda-forge::numpy=1.19.4'

    input:
    path csvfiles
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset)

    output:
    file '*.png'
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset), emit: vidarray

    script:
    if(params.refind_pairs) {
         """
         echo "MESSAGE: Processing ${name} with re-find pairs. This takes TIME with long videos."
#NEED TO CHECK IF FILES ARE PRESENT BEFORE DELETING, BUT MUST DELETE TO RE-DO ANALYSIS WITH NEW PARAMETERS
#         rm $baseDir/${params.VIDEO_DIR}/pairs/${name}_pair*.png
         select_pairs.py -p ${name} -v1 $baseDir/${params.VIDEO_DIR}/clips/${name}${VL}_cl_${start}_${end}_undis.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/${name}${VR}_cl_${start}_${end}_undis.mkv -f $baseDir/${params.VIDEO_DIR}/data/${name}_pairs.csv -e ${params.P_dist} -n ${params.P_n} -m ${params.P_move} -l ${params.watchvideo}
         """
    }else{
         """
         echo "Copying existing paired image files (.png) for ${name} "
         echo "\t\tfiles exist at $baseDir/${params.VIDEO_DIR}/pairs/${name}_pair*.png "
         cp $baseDir/${params.VIDEO_DIR}/pairs/${name}_pair*.png ./
         """
    }
}

process new_calibrate {
    publishDir "$params.DATA_DIR/stereo_maps"

    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'

    input:
    path pairs
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset)

    output:
    path '*.pkl'
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset),emit: vidarray

    script:
    
    if(params.recalc_left) {
         """
         new_calibrate.py -c ${params.checkdim} -sq ${params.squaresize} -l ${params.watchvideo} -pre ${name} -p $baseDir/${params.VIDEO_DIR}/pairs
         """
    }else{
         """
         cp $baseDir/${params.DATA_DIR}/stereo_maps/${name}_stereomap.pkl ./
         """
    }
}

process new_rectify {

    publishDir "$params.VIDEO_DIR/rectified"
    
    conda = 'conda-forge::opencv=4.5.0 conda-forge::numpy=1.19.4'
    
    input:
    tuple val(name), val(VL), val(VR), val(start), val(end), val(offset)
    
    output:
    path '*.mkv'
    
    script:
    """
    new_rectify.py -pp $baseDir/${params.DATA_DIR}/stereo_maps -v1 $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VL}_cl_${start}_${end}.mkv -v2 $baseDir/${params.VIDEO_DIR}/clips/cfr_${name}${VR}_cl_${start}_${end}.mkv -l 1 -pre ${name} -w ${params.watchvideo}

    """
   

}

