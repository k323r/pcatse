function accelerations_json2csv () {

    if ! [ -f $1 ] || [ -z $1 ] ; then
        echo "please provide a input json file"
    fi

    echo "timestamp,acc_x,acc_y,acc_z"
    cat $1 |
    jq -r '.imu | select( . != null ) | [ .timestamp, .acc_x, .acc_y, .acc_z] | @csv'
}

function imu_json2csv () {

    if ! [ -f $1 ] || [ -z $1 ] ; then
        echo "please provide a input json file"
    fi

    echo "timestamp,acc_x,acc_y,acc_z,rot_x,rot_y,rot_z,mag_x,mag_y,mag_z"
    cat $1 |
    jq -r '.imu | select( . != null ) | [ .timestamp, .acc_x, .acc_y, .acc_z, .rot_x, .rot_y, .rot_z, .mag_x, .mag_y, .mag_z ] | @csv'
}

function gnss_json2csv () {

    if ! [ -f $1 ] || [ -z $1 ] ; then
        echo "please provide a input json file"
    fi

    echo "timestamp,lat,lon,alt"
    cat $1 |
    jq -r '.gnss | select( . != null ) | [ .timestamp, .lat, .lon, .alt ] | @csv'
}


