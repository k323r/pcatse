import random
import time
import uptime
from math import sin

class MPU9250():

    _linear_acceleration = dict()
    _rotational_acceleration = dict()
    _magnetic_field = dict()
    _time_ticks = 0.0
    _time_uptime = 0.0

    def __init__(self):
        self._linear_acceleration = {'x' : 0.0, 'y' : 0.0, 'z' : 0.0}
        self._rotational_acceleration = {'x' : 0.0, 'y' : 0.0, 'z' : 0.0}
        self._magnetic_field = {'x' : 0.0, 'y' : 0.0, 'z' : 0.0}
        
        self._update_time()

    def _update_linear_acceleration(self):
        self._linear_acceleration['x'] = sin(self._time_ticks)
        self._linear_acceleration['y'] = sin(self._time_ticks)
        self._linear_acceleration['z'] = sin(self._time_ticks)

    def _update_rotational_acceleration(self):
        self._rotational_acceleration['x'] = sin(self._time_ticks)
        self._rotational_acceleration['y'] = sin(self._time_ticks)
        self._rotational_acceleration['z'] = sin(self._time_ticks)

    def _update_magnetic_field(self):
        self._magnetic_field['x'] = sin(self._time_ticks)
        self._magnetic_field['y'] = sin(self._time_ticks)
        self._magnetic_field['z'] = sin(self._time_ticks)

    def _update_measurements(self):
        self._update_linear_acceleration()
        self._update_rotational_acceleration()
        self._update_magnetic_field()

    def _update_time(self):
        self._time_ticks = time.time()
        self._time_uptime = uptime.uptime()

    def get_data(self):
        self._update_measurements()
        self._update_time()

        return {'unixtime' : self._time_ticks,
                'uptime' : self._time_uptime, 
                'linear_acceleration' : self._linear_acceleration,
                'rotational_acceleration' : self._rotational_acceleration,
                'magnetic_field' : self._magnetic_field,
               }

if __name__ == '__main__':
    imu = MPU9250()
    while True:
        measurement = imu.get_data()
        print('{}'.format(measurement))
        time.sleep(0.1)