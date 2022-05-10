#!/bin/bash

counter=1
<<<<<<< HEAD
timeDirPattern="*.*"
sourceFileName="U_zNormal.vtk"
targetDirName=$(echo $sourceFileName | sed -s 's/\.vtk//')
=======
timeDirPattern="[1-9]*"
sourceFileName=""


if [ -z $1 ]
then
        echo "please provide the source file name"
        exit -1
else
        sourceFileName="$1"
        echo "$sourceFileName"
fi

targetDirName=$(echo $sourceFileName | sed -s 's/\.vtp//')
>>>>>>> f58b4cd1a968da370dc753949053d3e10f45b54b

echo $targetDirName

if [ -d time-sorted/${targetDirName} ]
then
<<<<<<< HEAD
        if [ $(ls time-sorted/${targetDirName}/*.vtk | wc -l) != 0 ]
        then
                rm time-sorted/${targetDirName}/*.vtk
=======
        if [ $(ls sortedSurfaces/${targetDirName}/*.vtp | wc -l) != 0 ]
        then
                rm sortedSurfaces/${targetDirName}/*.vtp
>>>>>>> f58b4cd1a968da370dc753949053d3e10f45b54b
        fi
else
        mkdir -p time-sorted/${targetDirName}
fi

for timeDir in sort -n $timeDirPattern
do
        if [ -d $timeDir ]
        then
            if [ -e ${timeDir}/${sourceFileName} ] && [ -f ${timeDir}/${sourceFileName} ]
            then
<<<<<<< HEAD
            targetPath="time-sorted/${targetDirName}/${targetDirName}_${counter}.vtk"
=======
            targetPath="sortedSurfaces/${targetDirName}/${targetDirName}_${counter}.vtp"
>>>>>>> f58b4cd1a968da370dc753949053d3e10f45b54b
            echo $targetPath
                    ln -s ../../${timeDir}/${sourceFileName} $targetPath
                    counter=$(($counter+1))
            fi
        fi
done

