#!/bin/bash

set -e

function help () {
cat<<EOL
$0 - creates vortex generator stls to be used with snappyHexMesh
EOL
exit -1
}

function print_baseline_vg () {

    vgfile="${output_dir}/basevg.stl"

    cat<<EOF>>$vgfile
solid vg
  facet normal 0 0 1
    outer loop
      vertex -0.5 -0.5 0
      vertex 0.5 0.5 0
      vertex -0.5 0.5 0
    endloop
  endfacet
  facet normal 0 0 1
    outer loop
      vertex -0.5 -0.5 0
      vertex 0.5 -0.5 0
      vertex 0.5 0.5 0
    endloop
  endfacet
endsolid vg
EOF

    echo $vgfile
}

function scale () {

    # default scale parameters
    scale_default="(0.01 0.01 1)"

    # check if a valid stl file has been provided
    infile=$1
    if ! [[ -f $infile ]]
    then
        echo "please provide a valid input file"
        help
    fi

    # set scale to the second function argument or fall back to default scale parameters
    if [[ -z $2 ]]
    then
        scale=$scale_default
    else
        scale=$2
    fi

    # create a new temporary file 
    tmpfile=$( mktemp "${output_dir}/scaled_XXX.stl" )

    # echo "scaling ${infile} by ${scale} and writing output to ${tmpfile}"

    # use surfaceTransformPoints to scale the STL and print output to temporary stl file
    surfaceTransformPoints -scale "${scale}" "${infile}" "${tmpfile}" > /dev/null

    # echo new stl file file name so that it can be captured in the function call
    echo ${tmpfile}
}

function translate () {

        translate_default="(0 0 0.015)"

        # check if a valid stl file has been provided
        infile=$1
        if ! [[ -f $infile ]]
        then
                echo "please provide a valid input file"
                help
        fi

        # set scale to the second function argument or fall back to default scale parameters
        if [[ -z $2 ]]
        then
                translate=$translate_default
        else
                translate=$2
        fi

        tmpfile=$( mktemp "${output_dir}/translated_XXX.stl")

        surfaceTransformPoints -translate "${translate}" "${infile}" "${tmpfile}" > /dev/null

        echo $tmpfile
}

function rotate () {
        
        # set default angle and axis
        angle_default="((0 1 0) 15)"
        angle=$angle_default

        infile=$1
        if ! [[ -f $infile ]]
        then
                echo "please provide a valid infile to be rotated"
                help
        fi
        
        # override default value if a second parameter is given
        if [[ $2 ]]
        then
                angle=$2
        fi

        tmpfile=$( mktemp "${output_dir}/rotated_XXX.stl")

        surfaceTransformPoints -rotate-angle "${angle}" "${infile}" "${tmpfile}" > /dev/null

        echo $tmpfile
        
}

function create_vg () {
 
        translate_posY_distance=$(python -c "print($vg_height/2.0)")
        translate_posZ_distance=$(python -c "print($vg_pair_distance/2)")
        translate_negZ_distance=$(python -c "print(($vg_pair_distance/2)*-1)")

        scale_vg="(${vg_length} ${bl_height} 1)"
        rotate_aoa="((0 1 0) $vg_aoa)"
        counter_rotate="((0 1 0) $vg_aoa_cntr)"
        translate_cylinder_surface="(0 0.5 0)"
        translate_posY="(0 $translate_posY_distance 0)"
        translate_posZ="(0 0 $translate_posZ_distance)"
        translate_negZ="(0 0 $translate_negZ_distance)"
   
       
        # create baseline vg file
        vgfile=$(print_baseline_vg)
        echo "create baseline vg file: ${vgfile}"
        
        # scale to boundary layer dimensions
        scaled=$(scale "${vgfile}" "${scale_vg}")
        echo "created scaled vg file: ${scaled}"
        
        # translate vg to y=0 - curvature_offset
        translated=$(translate "${scaled}" "${translate_posY}")
        echo "created translated vg file: ${translated}"
        
        # rotate to angle of attack
        rotated=$(rotate "${translated}" "${rotate_aoa}")
        echo "created rotated vg file: ${rotated}"

        # if a pair of vortex generator is to be generated
        if [[ $mirror ]]
        then
                echo "mirroring vg to create vg pair"

                # create a second file
                cp $rotated "${output_dir}/rotated_cntr.stl"

                # rotate second stl in counter direction of original angle of attack
                rotated_cntr=$(rotate "${output_dir}/rotated_cntr.stl" "${counter_rotate}") 
                echo "rotated cntr: $rotated_cntr"
                
                # move vortex genertors symmetrically in z direction
                translated_posZ=$(translate "${rotated}" "${translate_posZ}")
                echo "lower vg $translated_posZ"
                translated_negZ=$(translate "${rotated_cntr}" "${translate_negZ}")
                echo "upper vg $translated_negZ"
        
                # remove old file, if present
                if [[ -e vg_final.stl ]]
                then
                        echo "removing old stl"
                        rm vg_final.stl
                fi
               
                # concatenate vortex generators into one file
                cat $translated_posZ $translated_negZ >> vg_final.stl
        else
                mv $rotated vg_final.stl
        fi
}

function main () {
        
        output_dir=$(mktemp -d "/tmp/create-vg_XXX")

        mirror=1 

        bl_height=0.015
        curvature_offset=0.001

        cylinder_length=4
        cylinder_diameter=1
        cylinder_radius=$(python -c "print($cylinder_diameter/2.0)")
 
        vg_height=$(python -c "print($bl_height*0.9)")
        vg_length=$(python -c "print($bl_height*2.5)")
        vg_aoa=-18
        vg_aoa_cntr=$(python -c "print($vg_aoa*-2)")
        vg_pair_distance=$(python -c "print($bl_height*2.6666666666)")
        vg_spacing_spanwise=$(python -c "print($cylinder_diameter*0.1)")
        vg_spacing_circumference=180
        vg_offset_circumference=0
        translate_negY=$(python -c "print( ($cylinder_diameter + $vg_height) * -1)")

        spanwise_start=$(python -c "print(($cylinder_length/2)*-1)")
        spanwise_end=$(python -c "print($cylinder_length/2)")

        echo "boundary layer height: ${bl_height}"
        echo "vg heigth: ${vg_height}"
        echo "vg length: ${vg_length}"
        echo "vg aoa: ${vg_aoa}"
        echo "vg cunterrotating local distance: ${vg_pair_distance}"

        # create the vortex generator as a stl file in the current directory
        create_vg

        # 1. move vg to cylinder radius
        vg_file="${output_dir}/vg_final.stl"
        cp vg_final.stl $vg_file

        vg_cylinder_surface=$(translate "${vg_file}" "(0 ${cylinder_radius} 0)")

        echo "vg at cylinder surface: $vg_cylinder_surface"

        counter=0
        for span_i in $(seq $spanwise_start $vg_spacing_spanwise $spanwise_end)
        do
                counter=$((counter+=1))
                target_basename=$(basename $vg_cylinder_surface .stl)
                target_name="${output_dir}/${target_basename}_${counter}.stl"
                target_transformation="(0 0 ${span_i})"
                
                echo "translating ${vg_cylinder_surface} to ${target_transformation} as ${target_name}"

                surfaceTransformPoints -translate "${target_transformation}" "$vg_cylinder_surface" "$target_name" > /dev/null
        done

        cat "${output_dir}/${target_basename}"_*.stl > ${output_dir}/target_1.stl

        

        surfaceTransformPoints -translate "(0 $translate_negY 0)" "${output_dir}/target_1.stl" "${output_dir}/target_2.stl"
        cat "${output_dir}"/target_?.stl > vg_final.stl



        #for circ_i in $(seq 0 $vg_spacing_circumference 360)
        #do
        #        if [[ "$circ_i" -eq 0 ]] || [[ "$circ_i" -eq 360 ]]
        #        then
        #                echo "skipping ${circ_i}"
        #                continue
        #        fi
        #done

}

main

