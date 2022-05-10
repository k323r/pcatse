#!/bin/bash

counter=1
timeDirPattern="*.*"
sourceFileName="U_zNormal.vtk"
targetDirName=$(echo $sourceFileName | sed -s 's/\.vtk//')

echo $targetDirName

if [ -d time-sorted/${targetDirName} ]
then
        if [ $(ls time-sorted/${targetDirName}/*.vtk | wc -l) != 0 ]
        then
                rm time-sorted/${targetDirName}/*.vtk
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
            targetPath="time-sorted/${targetDirName}/${targetDirName}_${counter}.vtk"
            echo $targetPath
                    ln -s ../../${timeDir}/${sourceFileName} $targetPath
                    counter=$(($counter+1))
            fi
        fi
done

