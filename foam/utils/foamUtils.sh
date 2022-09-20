function executionTime () {
  (test -f $1 && echo "processing ${1}") || (echo "file ${1} does not exist")
  cat $1 | 
  grep -E "^ExecutionTime" | 
  awk 'NR>1{print $3-old; old=$3}'
}

function linkVTPs () {
  counter=0; for t in $(ls .. | sort -n)
  do
    if [[ "$t" == "timesorted" ]]
    then
      echo "skipping timesorted dir"
      continue
    fi
    for f in ../"${t}"/*
    do
      name=$(basename ../"${t}"/"${f}" .vtp)
      ln -s ../"${t}"/"${f}" "${name}_${counter}.vtp"
    done
    counter=$((counter += 1))
  done
}

function extractCentreOfMass () {
	test -f $1 || echo "${1} no such file or directory"
	echo "#time,x,y,z" > centreOfMass.csv

	cat $1 |
	grep -e "^Time" -A 11|
	while read line
	do
		time=$(echo "${line}" | grep -e "^Time")
		if ! [[ -z $time ]]
		then
			time=$(echo $time | cut -d" " -f3)
			echo -n $time >> centreOfMass.csv
		fi
		com=$(echo "${line}" | grep "Centre of mass")
		if ! [[ -z $com ]]
		then
			com=$(echo $com | cut -d: -f2 | sed -e "s/(//" -e "s/)//" -e "s/^\s//" -e "s/\s/,/g")
			echo ",${com}" >> centreOfMass.csv
		fi
	done

}

function extractLinearVelocity () {
	test -f $1 || echo "${1} no such file or directory"
	echo "#time,vx,vy,vz" > linearVelocity.csv

	cat $1 |
	grep -e "^Time" -A 15|
	while read line
	do
		time=$(echo "${line}" | grep -e "^Time")
		if ! [[ -z $time ]]
		then
			time=$(echo $time | cut -d" " -f3)
			echo -n $time >> linearVelocity.csv
		fi
		com=$(echo "${line}" | grep "Linear velocity")
		if ! [[ -z $com ]]
		then
			com=$(echo $com | cut -d: -f2 | sed -e "s/(//" -e "s/)//" -e "s/^\s//" -e "s/\s/,/g")
			echo ",${com}" >> linearVelocity.csv
		fi
	done

}



function extractVelocityOfMass () {
	test -f $1 || echo "${1} no such file or directory"
	echo "vx,vy,vz" > linearVelocity.csv
	cat $1 | 
	grep "Linear velocity" |
	cut -d: -f2 |
	sed -e "s/(//" -e "s/)//" -e "s/^\s//" -e "s/\s/,/g" >> linearVelocity.csv
}
