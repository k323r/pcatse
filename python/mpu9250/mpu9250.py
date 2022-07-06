# TODO
# - implement filter?
# - implement producer/consumer pattern with multiprocessing?

import smbus
import time
import uptime
from datetime import datetime, timezone

## MPU9250 Default I2C slave address
SLAVE_ADDRESS = 0x68
## AK8963 I2C slave address
AK8963_SLAVE_ADDRESS = 0x0C
## Device id
DEVICE_ID = 0x71

""" MPU-9250 Register Addresses """
## sample rate driver
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_CONFIG_2 = 0x1D
LP_ACCEL_ODR = 0x1E
WOM_THR = 0x1F
FIFO_EN = 0x23
I2C_MST_CTRL = 0x24
I2C_MST_STATUS = 0x36
INT_PIN_CFG = 0x37
INT_ENABLE = 0x38
INT_STATUS = 0x3A
ACCEL_OUT = 0x3B
TEMP_OUT = 0x41
GYRO_OUT = 0x43

I2C_MST_DELAY_CTRL = 0x67
SIGNAL_PATH_RESET = 0x68
MOT_DETECT_CTRL = 0x69
USER_CTRL = 0x6A
PWR_MGMT_1 = 0x6B
PWR_MGMT_2 = 0x6C
FIFO_R_W = 0x74
WHO_AM_I = 0x75

## Gyro Full Scale Select 250dps
GFS_250 = 0x00
## Gyro Full Scale Select 500dps
GFS_500 = 0x01
## Gyro Full Scale Select 1000dps
GFS_1000 = 0x02
## Gyro Full Scale Select 2000dps
GFS_2000 = 0x03
## Accel Full Scale Select 2G
AFS_2G = 0x00
## Accel Full Scale Select 4G
AFS_4G = 0x01
## Accel Full Scale Select 8G
AFS_8G = 0x02
## Accel Full Scale Select 16G
AFS_16G = 0x03

# AK8963 Register Addresses
AK8963_ST1 = 0x02
AK8963_MAGNET_OUT = 0x03
AK8963_CNTL1 = 0x0A
AK8963_CNTL2 = 0x0B
AK8963_ASAX = 0x10

# CNTL1 Mode select
## Power down mode
AK8963_MODE_DOWN = 0x00
## One shot data output
AK8963_MODE_ONE = 0x01

## Continous data output 8Hz
AK8963_MODE_C8HZ = 0x02
## Continous data output 100Hz
AK8963_MODE_C100HZ = 0x06

# Magneto Scale Select
## 14bit output
AK8963_BIT_14 = 0x00
## 16bit output
AK8963_BIT_16 = 0x01

## smbus
bus = smbus.SMBus(1)

## MPU9250 I2C Controll class
class MPU9250:

    address = 0x00
    _linear_acceleration_resolution = 0
    _rotational_acceleration_resolution = 0
    _magnetic_field_resolution = 0

    _linear_acceleration = dict()
    _rotational_acceleration = dict()
    _magnetic_field = dict()
    _magnetic_correction_coefficient = dict()
    _temperature = 0.0
    _time_unixtime = 0.0
    _time_uptime = 0.0

    ## Constructor
    #  @param [in] address MPU-9250 I2C slave address default:0x68
    def __init__(
        self,
        address=SLAVE_ADDRESS,
        linear_acceleration_resolution=AFS_2G,
        rotational_acceleration_resolution=GFS_250,
        magnetic_field_resolution=AK8963_BIT_16,
        magnetic_field_sensor_mode=AK8963_MODE_C8HZ,
    ):

        self._address = address
        self._magnetic_field_resolution = magnetic_field_resolution
        self._magnetic_field_sensor_mode = magnetic_field_sensor_mode

        self._linear_acceleration = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._rotational_acceleration = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._magnetic_field = {"x": 0.0, "y": 0.0, "z": 0.0}
        self._temperature = 0.0

        self._config_MPU9250(
            rotational_acceleration_resolution, linear_acceleration_resolution
        )
        # self._config_AK8963(self._magnetic_field_sensor_mode, self._magnetic_field_resolution)
        self._update_time()

    def get_data(self):

        self._read_linear_acceleration()
        self._read_rotational_acceleration()
        # self._read_magnetic_field()
        self._read_temperature()
        self._update_time()

        return [
            datetime.fromtimestamp(self._time_unixtime, tz=timezone.utc),
            self._time_unixtime,
            self._time_uptime,
            self._temperature,
            *[x for _, x in self._linear_acceleration.items()],
            *[x for _, x in self._rotational_acceleration.items()],
            *[x for _, x in self._magnetic_field.items()],
        ]
        # return {
        #    'timestamp'                  : self._time_unixtime,
        #    'uptime'                    : self._time_uptime,
        #    'temperature'               : self._temperature,
        #    'linear_acceleration'       : self._linear_acceleration,
        #    'rotational_acceleration'   : self._rotational_acceleration,
        #    'magnetic_field'            : self._magnetic_field,
        # }

    ## Search Device
    #  @param [in] self The object pointer.
    #  @retval true device connected
    #  @retval false device error
    def _search_device(self):
        who_am_i = bus.read_byte_data(self._address, WHO_AM_I)
        if who_am_i == DEVICE_ID:
            return True
        else:
            return False

    ## Configure MPU-9250
    #  @param [in] self The object pointer.
    #  @param [in] gfs Gyro Full Scale Select(default:GFS_250[+250dps])
    #  @param [in] afs Accel Full Scale Select(default:AFS_2G[2g])
    def _config_MPU9250(self, gfs, afs):
        if gfs == GFS_250:
            self._rotational_acceleration_resolution = 250.0 / 32768.0
        elif gfs == GFS_500:
            self._rotational_acceleration_resolution = 500.0 / 32768.0
        elif gfs == GFS_1000:
            self._rotational_acceleration_resolution = 1000.0 / 32768.0
        else:  # gfs == GFS_2000
            self._rotational_acceleration_resolution = 2000.0 / 32768.0

        if afs == AFS_2G:
            self._linear_acceleration_resolution = 2.0 / 32768.0
        elif afs == AFS_4G:
            self._linear_acceleration_resolution = 4.0 / 32768.0
        elif afs == AFS_8G:
            self._linear_acceleration_resolution = 8.0 / 32768.0
        else:  # afs == AFS_16G:
            self._linear_acceleration_resolution = 16.0 / 32768.0

        # sleep off
        bus.write_byte_data(self._address, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        # auto select clock source
        bus.write_byte_data(self._address, PWR_MGMT_1, 0x01)
        time.sleep(0.1)
        # DLPF_CFG
        bus.write_byte_data(self._address, CONFIG, 0x03)
        # sample rate divider
        bus.write_byte_data(self._address, SMPLRT_DIV, 0x04)
        # gyro full scale select
        bus.write_byte_data(self._address, GYRO_CONFIG, gfs << 3)
        # accel full scale select
        bus.write_byte_data(self._address, ACCEL_CONFIG, afs << 3)
        # A_DLPFCFG
        bus.write_byte_data(self._address, ACCEL_CONFIG_2, 0x03)
        # BYPASS_EN
        bus.write_byte_data(self._address, INT_PIN_CFG, 0x02)
        time.sleep(0.1)

    ## Configure AK8963
    #  @param [in] self The object pointer.
    #  @param [in] mode Magneto Mode Select(default:AK8963_MODE_C8HZ[Continous 8Hz])
    #  @param [in] mfs Magneto Scale Select(default:AK8963_BIT_16[16bit])
    def _config_AK8963(self, mode, mfs):
        self._magnetic_field_sensor_mode = mode

        if mfs == AK8963_BIT_14:
            self._magnetic_field_resolution = 4912.0 / 8190.0
        else:  #  mfs == AK8963_BIT_16:
            self._magnetic_field_resolution = 4912.0 / 32760.0

        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set read FuseROM mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x0F)
        time.sleep(0.01)

        # read coef data
        data = bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_ASAX, 3)

        self._magnetic_correction_coefficient = {
            "x": (data[0] - 128) / 256.0 + 1.0,
            "y": (data[1] - 128) / 256.0 + 1.0,
            "z": (data[2] - 128) / 256.0 + 1.0,
        }

        # set power down mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, 0x00)
        time.sleep(0.01)

        # set scale&continous mode
        bus.write_byte_data(AK8963_SLAVE_ADDRESS, AK8963_CNTL1, (mfs << 4 | mode))
        time.sleep(0.01)

    ## Read accelerometer
    #  @param [in] self The object pointer.
    def _read_linear_acceleration(self):
        data = bus.read_i2c_block_data(self._address, ACCEL_OUT, 6)

        self._linear_acceleration = {
            "x": round(
                self._data_conv(data[1], data[0])
                * self._linear_acceleration_resolution,
                6,
            ),
            "y": round(
                self._data_conv(data[3], data[2])
                * self._linear_acceleration_resolution,
                6,
            ),
            "z": round(
                self._data_conv(data[5], data[4])
                * self._linear_acceleration_resolution,
                6,
            ),
        }

    ## Read gyro
    #  @param [in] self The object pointer.
    def _read_rotational_acceleration(self):
        data = bus.read_i2c_block_data(self._address, GYRO_OUT, 6)

        self._rotational_acceleration = {
            "x": round(
                self._data_conv(data[1], data[0])
                * self._rotational_acceleration_resolution,
                6,
            ),
            "y": round(
                self._data_conv(data[3], data[2])
                * self._rotational_acceleration_resolution,
                6,
            ),
            "z": round(
                self._data_conv(data[5], data[4])
                * self._rotational_acceleration_resolution,
                6,
            ),
        }

    ## Read magneto
    #  @param [in] self The object pointer.
    def _read_magnetic_field(self):

        # check data ready
        drdy = bus.read_byte_data(AK8963_SLAVE_ADDRESS, AK8963_ST1)
        if drdy & 0x01:
            data = bus.read_i2c_block_data(AK8963_SLAVE_ADDRESS, AK8963_MAGNET_OUT, 7)

            # check overflow
            if (data[6] & 0x08) != 0x08:
                self._magnetic_field = {
                    "x": round(
                        self._data_conv(data[0], data[1])
                        * self._magnetic_field_resolution
                        * self._magnetic_correction_coefficient["x"],
                        6,
                    ),
                    "y": round(
                        self._data_conv(data[2], data[3])
                        * self._magnetic_field_resolution
                        * self._magnetic_correction_coefficient["y"],
                        6,
                    ),
                    "z": round(
                        self._data_conv(data[4], data[5])
                        * self._magnetic_field_resolution
                        * self._magnetic_correction_coefficient["z"],
                        6,
                    ),
                }

    ## Read temperature
    #  @param [out] temperature temperature(degrees C)
    def _read_temperature(self):
        data = bus.read_i2c_block_data(self._address, TEMP_OUT, 2)
        temp = self._data_conv(data[1], data[0])

        self._temperature = round((temp / 333.87 + 21.0), 3)

    ## Data Convert
    # @param [in] self The object pointer.
    # @param [in] data1 LSB
    # @param [in] data2 MSB
    # @retval Value MSB+LSB(int 16bit)
    def _data_conv(self, data1, data2):
        value = data1 | (data2 << 8)
        if value & (1 << 16 - 1):
            value -= 1 << 16
        return value

    ## Log time stamps
    # @param [in] self The object pointer
    def _update_time(self):
        self._time_unixtime = time.time()
        self._time_uptime = uptime.uptime()


if __name__ == "__main__":
    mpu = MPU9250()
    delta_t = 0.02
    while True:
        t = time.monotonic()
        print(",".join(map(str, mpu.get_data())))
        while time.monotonic() < t + delta_t:
            time.sleep(0.001)
