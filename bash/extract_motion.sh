#!/bin/bash

log=$1

function usage() {
cat<<EOL

extract_motion.sh logfile

extracts the motion of a body from an openfoam log file

EOL
exit -1
}

if ! [[ -f $log ]]
then
        echo "not a file: $log"
        usage
fi

#echo "time " > time.csv
#echo "x y z" > position-of-mass.csv
#echo " vx vy vz" > velocity-of-mass.csv

cat "$log" |
        grep -e "^Time = " -A15 |
        grep -e "^Time = " |
        cut -d ' ' -f 3 > time.csv

cat "$log" |
        grep -e "^Time = " -A15 |
        grep -e "Centre of mass" |
        cut -d ' ' -f 8-  | 
        sed -e 's/(//g' -e 's/)//g' > position-of-mass.csv

cat "$log" |
        grep -e "^Time = " -A15 |
        grep -e "Linear velocity" | 
        cut -d' ' -f 7- | 
        sed -e 's/(//g' -e 's/)//' > velocity-of-mass.csv


#cat "$log" |
#        grep -e "^Time = " | 
#        cut -d ' ' -f 3 > time.csv

#cat "$log" | 
#        grep -e "Centre of mass" | 
#        cut -d ' ' -f 8-10 | 
#        sed -e 's/(//g' -e 's/)//g' > centre-of-mass.csv

#cat "$log" | 
#        grep -e "Linear velocity" | 
#        cut -d' ' -f 7-9 | 
#        sed -e 's/(//g' -e 's/)//' > velocity-of-mass.csv

echo "time x y z vx vy vz" > motion.csv
paste -d ' ' time.csv position-of-mass.csv velocity-of-mass.csv >> motion.csv
rm time.csv position-of-mass.csv velocity-of-mass.csv

