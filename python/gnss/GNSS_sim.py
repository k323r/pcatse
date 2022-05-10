import os
import sys
import serial
import pynmea2
import time
import uptime

class GNSS_receiver():

    _BAUD_RATE = 0
    _SERIAL_PATH = ""
    _msg = ''
    _time_unixtime = 0.0
    _time_uptime = 0.0

    def __init__(self, baud_rate=9600, serial_path='/dev/ttyS0'):
        self._BAUD_RATE = baud_rate
        self._SERIAL_PATH = serial_path
        self._generate_test_GPGGA_sentence()

        """
        later:
        - parse config file
        - create a serial object and initiate
        - start a thread to constantly update gps data
        """
    
    def _generate_test_GPGGA_sentence(self):
        self._msg = pynmea2.GGA('GP', 
                                'GGA', 
                                (time.strftime('%H%M%S.00', time.gmtime()), 
                                '5303.00', 
                                'N', 
                                '0680.00', 
                                'E', 
                                '1', 
                                '04', 
                                '2.6', 
                                '100.00',
                                'M', 
                                '-33.9', 
                                'M', 
                                '', 
                                '0000',
                                ))
        self._time_unixtime = time.time()
        self._time_uptime = uptime.uptime()
    
    def get_data(self):

        self._generate_test_GPGGA_sentence() # needs to be executed in order to update _msg

        """
        In a later version, a thread should be started to regularly update GNSS data
        maybe via multiprocessing?
        """

        if self._msg.is_valid:
            return {
                'unixtime' : self._time_unixtime,
                'uptime' : self._time_uptime,
                'gnsstime' : str(self._msg.timestamp),
                'latitude' : self._msg.latitude,
                'longitude' : self._msg.longitude,
                'altitude' : self._msg.altitude,
            }
        else:
            return None