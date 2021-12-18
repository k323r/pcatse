#!/bin/bash

counter=1
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

echo $targetDirName

if [ -d sortedSurfaces/${targetDirName} ]
then
        if [ $(ls sortedSurfaces/${targetDirName}/*.vtp | wc -l) != 0 ]
        then
                rm sortedSurfaces/${targetDirName}/*.vtp
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
            targetPath="sortedSurfaces/${targetDirName}/${targetDirName}_${counter}.vtp"
            echo $targetPath
                    ln -s ../../${timeDir}/${sourceFileName} $targetPath
                    counter=$(($counter+1))
            fi
        fi
done

