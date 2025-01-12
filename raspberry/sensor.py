from adafruit_mmc56x3 import MMC5603  # type: ignore
from adafruit_lsm6ds.lsm6ds3trc import LSM6DS3TRC  # type: ignore
from adafruit_lsm6ds import GyroRange, AccelRange, Rate  # type: ignore
import numpy as np
import time

from calibration import calibration, full_calibration
from calibration import SIM1, SIM2, HIM1, HIM2


class Sensor:
    """
    Class to handle the sensor data. from the accelerometer, gyroscope and magnetometer.
    """
    def __init__(self, i2c, stick_id=1):
        self.magnetometer = MMC5603(i2c)
        self.inertial = LSM6DS3TRC(i2c)
        self.HIG = self.get_gyro_calibration()
        self.stick_id = stick_id
        self.HIM = HIM1 if stick_id == 1 else HIM2
        self.SIM = SIM1 if stick_id == 1 else SIM2

    def __str__(self):
        return str(self.stick_id)

    def set_rate_208(self):
        """
        Set the data rate of the sensors to 208 Hz.
        """
        self.inertial.accelerometer_data_rate = Rate.RATE_208_HZ
        self.inertial.gyro_data_rate = Rate.RATE_208_HZ
        self.magnetometer.data_rate = 208

    def set_range_8g_2000dps(self):
        """ 
        Set the range of the sensors to 8g and 2000 dps.
        """
        self.inertial.accelerometer_range = AccelRange.RANGE_8G
        self.inertial.gyro_range = GyroRange.RANGE_2000_DPS

    def get_gyro_calibration(self):
        """
        Calibrate the gyroscope by taking the mean of the first 500 samples after skipping 500 samples.
        """
        x = np.zeros((1000,), dtype=np.float32)
        y = np.zeros((1000,), dtype=np.float32)
        z = np.zeros((1000,), dtype=np.float32)
        for i in range(1000):
            gyro_x, gyro_y, gyro_z = self.inertial.gyro
            x[i] = gyro_x
            y[i] = gyro_y
            z[i] = gyro_z

        e_x = np.mean(x[500:], axis=0)
        e_y = np.mean(y[500:], axis=0)
        e_z = np.mean(z[500:], axis=0)
        return np.array([e_x, e_y, e_z])

    def get_raw(self):
        acc = np.array(self.inertial.acceleration)
        gyr = np.array(self.inertial.gyro)
        mag = np.array(self.magnetometer.magnetic)

        return acc, gyr, mag

    def get_calibrated(self):
        """
        get the calibrated data from the sensors.
        """
        acc, gyr, mag = self.get_raw()

        gyr = calibration(gyr, self.HIG)
        mag = full_calibration(mag, self.SIM, self.HIM)

        return [acc, gyr, mag]

    def get_calibrated_str(self):
        """
        Get valid data in string format to be sent by the server.
        """
        acc, gyr, mag = self.get_calibrated()

        mag_x, mag_y, mag_z = mag
        accel_x, accel_y, accel_z = acc
        gyro_x, gyro_y, gyro_z = gyr

        data = f"{mag_x:15.6f};{mag_y:15.6f};{mag_z:15.6f};{accel_x:15.6f};
        {accel_y:15.6f};{accel_z:15.6f};{gyro_x:15.6f};{gyro_y:15.6f};{gyro_z:15.6f};{time.time():50}"

        return data
