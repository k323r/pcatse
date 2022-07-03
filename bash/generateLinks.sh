#!/bin/bash

counter=1
timeDirPattern="[1-9]*"
sourceFileName=""
baseTargetDir="time-sorted"


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

if [ -d ${baseTargetDir}/${targetDirName} ]
then
        if [ $(ls ${baseTargetDir}/${targetDirName}/*.vtp | wc -l) != 0 ]
        then
                rm ${baseTargetDir}/${targetDirName}/*.vtp
        fi
else
        mkdir -p ${baseTargetDir}/${targetDirName}
fi

for timeDir in sort -n $timeDirPattern
do
        if [ -d $timeDir ]
        then
            if [ -e ${timeDir}/${sourceFileName} ] && [ -f ${timeDir}/${sourceFileName} ]
            then
            targetPath="${baseTargetDir}/${targetDirName}/${targetDirName}_${counter}.vtp"
            echo $targetPath
                    ln -s ../../${timeDir}/${sourceFileName} $targetPath
                    counter=$(($counter+1))
            fi
        fi
done

