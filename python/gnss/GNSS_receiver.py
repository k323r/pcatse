import os
import sys
import serial
from serial import SerialException
import pynmea2
from pynmea2 import ParseError
import time
import uptime
from multiprocessing import Queue, Process

def generate_test_GPGGA_sentence(self):
    msg = pynmea2.GGA('GP', 
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
    return msg

class GNSS_receiver():

    baud_rate = 0
    serial_port = ""
    _time_unixtime = 0
    _time_uptime = 0.0
    #                  FIX       DATUM     LAT/LON  DATE/TIME
    _NMEA_SENTENCES = ('GPGGA,', 'GPDTM,', 'GPGLL', 'GPZDA,')
    
    def __init__(self, serial_baud_rate=9600, serial_port='/dev/ttyS0'):
    
        self.serial_baud_rate = serial_baud_rate
        self.serial_port = serial_port
        self._time_unixtime = time.time()
        self._time_uptime = uptime.uptime()

        try:
            self.serial_bus = serial.Serial(port=self.serial_port, baudrate=self.serial_baud_rate)
        
        except FileNotFoundError:
            print('* GNSS.py: not a valid serial port: {}'.format(self.serial_port))
            print('* GNSS.py: bye')
            sys.exit()

        except PermissionError:
            print('* GNSS.py: please check user permission to access {}'.format(self.serial_port))
            print('* bye')
            sys.exit()

        except SerialException as se:
            print('* GNSS.py: failed to instantiate serial object: {}'.format(se))
            print('* GNSS.py: bye')
            sys.exit()
        # check settings -> memory limitation, ring buffer?

        self._serial_queue = Queue()
        self._reading_process = Process(target=self._reader,)

    def __del__(self):
        if hasattr(self, '_reading_process'):
            print('* GNSS.py: terminating reader process')
            try:
                self._reading_process.terminate()
            except Exception as e:
                print('* GNSS.py: termination of reader process failed: {}'.format(e))
                print('* GNSS.py: sending SIGKILL')
                self._reading_process.kill()

        if hasattr(self, '_serial_queue'):
            print('* GNSS.py: terminating reader queue')
            try:
                self._serial_queue.close()
            except Exception as e:
                print('* GNSS.py: failed to close serial reader queue')

        if hasattr(self, 'serial_bus'):
            print('* GNSS.py: terminating serial bus')
            try:
                self.serial_bus.close()
            except Exception as e:
                print('* GNSS.py: failed to close serial bus!')
        

    def run(self):
        print('* GNSS.py: starting serial reading process')
        self._reading_process.start()


    def _reader(self):
        while True:

            # read data from serial
            try:
                data = self.serial_bus.readline().decode('utf-8')
                self._time_unixtime = time.time()
                self._time_uptime = uptime.uptime()
            except Exception as e:
                print('* GNSS.py: failed to read from serial bus')
                continue
            
            # try to parse nmea sentence
            try:
                data= pynmea2.parse(data)
            except ParseError:
                print('* GNSS.py: failed to parse NMEA sentence')
                continue
            except Exception as e:
                print('* GNSS.py: unexpected exception occured: {}'.format(e))
                sys.exit()

            # try to push parsed data onto the queue
            # TODO add support to choose only certain types of nmea sentences
            # also: the current implementation is probably not going to be very perfomant
           
            # skip non-interesting NMEA sentences
            if data.identifier() not in self._NMEA_SENTENCES:
                continue
            
            try:
                self._serial_queue.put({'unixtime' : self._time_unixtime,
                                        'uptime' : self._time_uptime,
                                        'nmea_sentence' : data.__dict__,
                                        })
            except Exception as e:
                print('* GNSS.py: failed to push data into queue')
                continue

            time.sleep(0.1)
    
    def get_data(self):
        # pop data from the queue
        return [self._serial_queue.get_nowait() for _ in range(self._serial_queue.qsize())]
        
