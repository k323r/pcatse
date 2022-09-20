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

function extractCentreOfMass2 () {
	test -f $1 || echo "${1} no such file or directory"
	echo "#time,x,y,z" > centreOfMass.csv

	cat $1 |
	while read line
	do
		time=$(echo $line | grep -e "^Time")
		if ! [[ -z $time ]]
		then
			time=$(echo $time | cut -d" " -f3)
			flag=0
			echo -n "${time}," >> centreOfMass.csv
		fi

		com=$(echo "${line}" | grep "Centre of mass")
                if ! [[ -z $com ]] && [[ "${flag}" -eq 0 ]]
                then
                        com=$(echo $com | cut -d: -f2 | sed -e "s/(//" -e "s/)//" -e "s/^\s//" -e "s/\s/,/g")
                        flag=1
			echo "${com}" >> centreOfMass.csv
		fi
	done

}

function extractCentreOfMass3 () {
	test -f $1 || (echo "no such file or directory: $1" && return)
	cat $1 |
	grep -e "^Time = " | cut -d" " -f3 > /tmp/time.log
	cat $1 |
	grep -e "^Time = " -A 11 | grep "Centre of mass" | cut -d: -f2 | sed -e "s/(//" -e "s/)//" -e "s/^\s//" -e "s/\s/,/g" > /tmp/com.log
	echo "time,x,y,z" > centreOfMass.csv
	paste -d, /tmp/time.log /tmp/com.log >> centreOfMass.csv
	rm /tmp/time.log
	rm /tmp/com.log
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
		vel=$(echo "${line}" | grep "Linear velocity")
		if ! [[ -z $vel ]]
		then
			vel=$(echo $vel | cut -d: -f2 | sed -e "s/(//" -e "s/)//" -e "s/^\s//" -e "s/\s/,/g")
			echo ",${vel}" >> linearVelocity.csv
		fi
	done

}

function extractLinearVelocity2 () {
	test -f $1 || (echo "no such file or directory: $1" && return)
	cat $1 |
	grep -e "^Time = " | cut -d" " -f3 > /tmp/time.log
	cat $1 |
	grep -e "^Time = " -A 15 | grep "Linear velocity" | cut -d: -f2 | sed -e "s/(//" -e "s/)//" -e "s/^\s//" -e "s/\s/,/g" > /tmp/vel.log
	echo "time,vx,vy,vz" > linearVelocity.csv
	paste -d, /tmp/time.log /tmp/vel.log >> linearVelocity.csv
	rm /tmp/time.log
	rm /tmp/vel.log
}


