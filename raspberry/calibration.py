import numpy as np

SIM = np.array(
    [[0.996, -0.005, -0.005], [-0.005, 0.998, 0.042], [-0.005, 0.042, 1.007]]
)

HIM = np.array([6.47, 8.8, -91.88])


def magnetic_calibration(uncalibrated, soft_iron_matrix=SIM, hard_iron_offset=HIM):
    """
    Calibrates a magnetic vector using the soft iron matrix and hard iron offset.

    Args:
        uncalibrated (numpy.ndarray): Uncalibrated magnetic vector (1D array of length 3).
        soft_iron_matrix (numpy.ndarray): Soft iron calibration matrix (3x3 array).
        hard_iron_offset (numpy.ndarray): Hard iron offset vector (1D array of length 3).

    Returns:
        numpy.ndarray: Calibrated magnetic vector (1D array of length 3).
    """
    return np.dot(soft_iron_matrix, uncalibrated - hard_iron_offset)


def gyro_calibration(uncalibrated):
    return uncalibrated


def acc_calibration(uncalibrated):
    return uncalibrated
