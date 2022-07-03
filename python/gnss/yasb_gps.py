# TODO
# - add argument parser
# - add configuration parserzs
# - add time functionality

import sys
import os
import signal
import time
import json
import argparse
import fcntl        # needed to open fifos non-blocking

from os import path

from .GNSS_receiver import GNSS_receiver

GPS_SERIAL_DIR = '/dev'
GPS_SERIAL_NAME = 'ttyS0'
GPS_BAUD_RATE = 9600
GPS_SERIAL_PATH = path.join(GPS_SERIAL_DIR, GPS_SERIAL_NAME)

GPS_FIFO_NAME = 'yasb-gps-fifo'
GPS_FIFO_DIR = '/tmp'
GPS_FIFO_PATH = path.join(GPS_FIFO_DIR, GPS_FIFO_NAME)

FIFO_REOPEN_LIMIT = 10

def signal_handler_exit(sig, frame):
    
    print('* yasb-gps: bye')
    sys.exit(0)

def create_fifo(fifo_path):
    if not path.exists(fifo_path):
        try:
            os.mkfifo(fifo_path)
        except Exception as e:
            print('* yasb-gps: failed to create gps fifo: {}'.format(e))
            sys.exit()
    else:
        print('* yasb-gps: fifo exists, skipping')

def open_fifo(fifo_path, mode='w'):

    try:
        fifo_out = open(fifo_path, mode)
    except Exception as e:
        print('* yasb-gps: failed to open fifo: {}'.format(e))
        sys.exit()

    return fifo_out


def yasb_gps_run():
    fifo_closed_counter = 0

    print("* yasb-gps: hello")

    gps = GNSS_receiver(serial_baud_rate=GPS_BAUD_RATE, 
                        serial_port=GPS_SERIAL_PATH
                       )

   
    # register signal handler for SIGINT (CTRL-C)
    print('* yasb-gps: trying to create fifo: {}'.format(GPS_FIFO_PATH)) 
    create_fifo(fifo_path=GPS_FIFO_PATH)
    
    print('* yasb-gps: trying to open fifo: {}'.format(GPS_FIFO_PATH))
    gps_fifo = open_fifo(fifo_path=GPS_FIFO_PATH)

    # only start the reading process after the fifo has successfully been opened
    print('* yasb-gps: starting reader process')
    gps.run()
 
    # start endless loop to read data from serial device
    print('* yasb-gps: entering consumer loop')
    while True:
        # get list of gps records
        gps_data = gps.get_data()

        if not gps_data:
            continue
        
        # temporary list used to store serialized data
        gps_data_json = list()

        # iterate over gps records and try to serialize to json
        for record in gps_data:
           try:
                gps_data_json.append(json.dumps(record))
           except TypeError:
                print('* yasb-gps: failed to dump data: {}'.format(record))
                continue
        
        # write out records to fifo
        try:
            for record in gps_data_json:
                gps_fifo.write('{}\n'.format(record))

            gps_fifo.flush()

        except KeyboardInterrupt:
            gps_fifo.close()
            del(gps)
            print('* yasb-gps: bye')
            sys.exit()

        except BrokenPipeError:
            print('* yasb-gps: fifo was closed by consumer, reopening')
            if fifo_closed_counter < FIFO_REOPEN_LIMIT:
                gps_fifo = open_fifo(GPS_FIFO_PATH)
                fifo_closed_counter += 1
            else:
                print('* yasb-imu: fifo was reopend more than {}x, stopping retries'.format(FIFO_REOPEN_LIMIT)) 
                del(gps)
                sys.exit()
        time.sleep(1)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler_exit)
    yasb_gps_run()
    

