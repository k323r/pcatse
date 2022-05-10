# TODO
# - configuration parser
# - argument parser

import argparse
import time 
import sys
import os
import json
import signal

from os import path

# from MPU9250_sim import MPU9250
from MPU9250 import MPU9250

IMU_FIFO_NAME = 'yasb-imu-fifo'
IMU_FIFO_DIR = '/tmp'
IMU_FIFO_PATH = path.join(IMU_FIFO_DIR, IMU_FIFO_NAME)

FIFO_REOPEN_LIMIT = 10

def signal_handler_exit(sig, frame):
    print('* yasb-imu: bye')
    sys.exit(0)

def create_fifo(fifo_path):
    if not path.exists(fifo_path):
        try:
            os.mkfifo(fifo_path)
        except Exception as e:
            print('* yasb-imu: failed to create gps fifo: {}'.format(e))
            sys.exit()
    else:
        print('* yasb-imu: fifo exists, skipping')

def open_fifo(fifo_path):
    try:
        fifo_out = open(fifo_path, 'w')
    except Exception as e:
        print('* yasb-imu: failed to open fifo: {}'.format(e))
        sys.exit()

    return fifo_out

def yasb_imu_run():
    fifo_closed_counter = 0

    # register signal handler for dealing with Ctrl+C

    print("* yasb-imu: hello")

    imu = MPU9250()

    print("* successfully create ICM20948 object")
    
    create_fifo(IMU_FIFO_PATH)
    fifo_out = open_fifo(IMU_FIFO_PATH)
    
    while True:
        sendstring = json.dumps(imu.get_data())
        try:
            fifo_out.write('{}\n'.format(sendstring))
            fifo_out.flush()
        except KeyboardInterrupt:
            fifo_out.close()
            print('* yasb-imu: okbye')
            sys.exit()

        except BrokenPipeError:
            print('* yasb-imu: fifo was closed by consumer, reopening')
            if fifo_closed_counter < FIFO_REOPEN_LIMIT:
                fifo_out = open_fifo(IMU_FIFO_PATH)
                fifo_closed_counter += 1
            else:
                print('* yasb-imu: fifo was reopend more than {}x, stopping retries'.format(FIFO_REOPEN_LIMIT)) 
                sys.exit()
        # needs to be called in order to get data into
        # yasb-fusionlog in realtime
        time.sleep(0.02)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler_exit)
    yasb_imu_run()
        
