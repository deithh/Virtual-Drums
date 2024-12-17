from adafruit_mmc56x3 import MMC5603
from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC
from adafruit_lsm6ds import GyroRange, AccelRange, Rate
import numpy as np
import time

from calibration import magnetic_calibration, gyro_calibration, acc_calibration


class Sensor:
    def __init__(self, i2c):
        self.magnetometer = MMC5603(i2c)
        self.inertial = LSM6DS3TRC(i2c)

    def set_rate_208(self):
        self.inertial.accelerometer_data_rate = Rate.RATE_208_HZ
        self.inertial.gyro_data_rate = Rate.RATE_208_HZ
        self.magnetometer.data_rate = 208

    def set_range_8g_2000dps(self):
        self.inertial.accelerometer_range = AccelRange.RANGE_8G
        self.inertial.gyro_range = GyroRange.RANGE_2000_DPS

    def get_raw(self):
        """
        return:
            -(accelerometer (np.ndarray), gyroscope (np.ndarray), magnetometer (np.ndarray)))
        """
        acc = np.array(self.inertial.acceleration)
        gyr = np.array(self.inertial.gyro)
        mag = np.array(self.magnetometer.magnetic)

        return acc, gyr, mag

    def get_calibrated(self):
        acc, gyr, mag = self.get_raw()
        acc = acc_calibration(acc)
        gyr = gyro_calibration(gyr)
        mag = magnetic_calibration(mag)

        return acc, gyr, mag

    def get_calibrated_str(self):

        acc, gyr, mag = self.get_calibrated()

        mag_x, mag_y, mag_z = mag
        accel_x, accel_y, accel_z = acc
        gyro_x, gyro_y, gyro_z = gyr

        data = f"{mag_x:15.6f};{mag_y:15.6f};{mag_z:15.6f};{accel_x:15.6f};{accel_y:15.6f};{accel_z:15.6f};{gyro_x:15.6f};{gyro_y:15.6f};{gyro_z:15.6f};{time.time():50}"
        return data
