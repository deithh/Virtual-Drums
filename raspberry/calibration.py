import numpy as np

SIM1 = np.array(
    [[0.999, 0.007, -0.001], [-0.007, 0.998, 0.026], [-0.001, 0.026, 1.004]]
)

HIM1 = np.array([8.59, 8.74, -96.99])

SIM2 = np.array([[0.999, -0.003, 0.006], [-0.003, 1.005, 0.029], [0.006, 0.029, 0.997]])
HIM2 = np.array([35.30, 12.35, -75.46])


def full_calibration(uncalibrated, soft_iron_matrix, hard_iron_offset):
    """
    Calibrates a  vector using the soft iron matrix and hard iron offset.
    """
    return np.dot(soft_iron_matrix, uncalibrated - hard_iron_offset)


def calibration(uncalibrated, hard_iron_offset):
    """
    Calibrates a  vector using the hard iron offset.
    """
    return uncalibrated - hard_iron_offset
