#!/bin/bash

counter=1
timeDirPattern="10*.*"
sourceFileName="U_zNormal.vtk"
targetDirName=$(echo $sourceFileName | sed -s 's/\.vtk//')

echo $targetDirName

if [ -d sortedSurfaces/${targetDirName} ]
then
        if [ $(ls sortedSurfaces/${targetDirName}/*.vtk | wc -l) != 0 ]
        then
                rm sortedSurfaces/${targetDirName}/*.vtk
        fi
else
        mkdir -p sortedSurfaces/${targetDirName}
fi

for timeDir in sort -n $timeDirPattern
do
        if [ -d $timeDir ]
        then
            if [ -e ${timeDir}/${sourceFileName} ] && [ -f ${timeDir}/${sourceFileName} ]
            then
            targetPath="sortedSurfaces/${targetDirName}/${targetDirName}_${counter}.vtk"
            echo $targetPath
                    ln -s ../../${timeDir}/${sourceFileName} $targetPath
                    counter=$(($counter+1))
            fi
        fi
done

