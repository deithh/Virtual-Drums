import numpy as np

SIM1 = np.array(
    [[0.999, 0.007, -0.001], [-0.007, 0.998, 0.026], [-0.001, 0.026, 1.004]]
)

HIM1 = np.array([8.59, 8.74, -96.99])

SIM2 = np.array(
    [[0.999, -0.003, 0.006], [-0.003, 1.005, 0.029], [0.006, 0.029, 0.997]]
)

HIM2 = np.array([35.30, 12.35, -75.46])

def magnetic_calibration(uncalibrated, stick_id):
    """
    Calibrates a magnetic vector using the soft iron matrix and hard iron offset.

    Args:
        uncalibrated (numpy.ndarray): Uncalibrated magnetic vector (1D array of length 3).
        soft_iron_matrix (numpy.ndarray): Soft iron calibration matrix (3x3 array).
        hard_iron_offset (numpy.ndarray): Hard iron offset vector (1D array of length 3).

    Returns:
        numpy.ndarray: Calibrated magnetic vector (1D array of length 3).
    """

    soft_iron_matrix = SIM1 if stick_id == 1 else SIM2
    hard_iron_offset = HIM1 if stick_id == 1 else HIM2

    return np.dot(soft_iron_matrix, uncalibrated - hard_iron_offset)


def gyro_calibration(uncalibrated, HIG):
    return uncalibrated - HIG 


def acc_calibration(uncalibrated):
    return uncalibrated