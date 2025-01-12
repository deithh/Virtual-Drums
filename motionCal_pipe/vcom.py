import numpy as np
import serial
import socket


def clear_data(row: str):
    """
    Parse sensor data

    Args:
        -row (str): A semicolon-separated string containing sensor data. The string should
                have the following format:
                "mag_x;mag_y;mag_z;acc_x;acc_y;acc_z;gyr_x;gyr_y;gyr_z;timestamp".
                Spaces within the string are ignored.

    Returns:
        tuple: A tuple containing four elements:
            - mag (numpy.ndarray): A calibrated 3-element array of magnetic field data [mag_x, mag_y, mag_z].
            - acc (numpy.ndarray): A 3-element array of accelerometer data [acc_x, acc_y, acc_z].
            - gyr (numpy.ndarray): A 3-element array of gyroscope data [gyr_x, gyr_y, gyr_z].
            - time (float): The timestamp extracted from the input data.
    """

    row = row.replace(" ", "")
    row = list(map(float, row.split(";")))

    mag = np.asarray(row[:3])
    acc = np.asarray(row[3:6])
    gyr = np.asarray(row[6:9])

    time = row[-1]

    return mag, acc, gyr, time


def serial_send_data(mag, acc, gyr, serial):
    """
    Prepare and send data over given serial port

    Args:
        - mag (numpy.ndarray): A calibrated 3-element array of magnetic field data [mag_x, mag_y, mag_z].
        - acc (numpy.ndarray): A 3-element array of accelerometer data [acc_x, acc_y, acc_z].
        - gyr (numpy.ndarray): A 3-element array of gyroscope data [gyr_x, gyr_y, gyr_z].
        - seiral (Serial): Opened serial port (pyserial)

    Returns:
        -(int) size of sent data

    """

    acc_scaled = (acc * 8192 / 9.8).astype(int)
    gyr_scaled = (gyr * 10).astype(int)
    mag_scaled = (mag * 10).astype(int)

    Acc_x, Acc_y, Acc_z = acc_scaled
    Gyro_x, Gyro_y, Gyro_z = gyr_scaled
    mag_x, mag_y, mag_z = mag_scaled

    to_serial_port = "Raw:{},{},{},{},{},{},{},{},{}\r\n".format(
        Acc_x, Acc_y, Acc_z, Gyro_x, Gyro_y, Gyro_z, mag_x, mag_y, mag_z
    )

    return serial.write(bytes(to_serial_port, "UTF-8"))


def udp_server(
    host="192.168.1.14", port=8080, baudrate=115200, com="COM1", message_size=195
):

    ser = serial.Serial(port=com, baudrate=baudrate)
    print(f"Serial communication established on at {baudrate} baud.")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        addr = ("192.168.1.14", 8080)
        # initial binding message
        client_socket.sendto("Hihi\n".encode("utf-8"), addr)
        print("Working..")
        while True:
            try:
                data, addr = client_socket.recvfrom(message_size)
                row = data.decode("utf-8")

                mag, acc, gyr, _ = clear_data(row)
                serial_send_data(mag, acc, gyr, ser)

            except Exception as e:
                print(f"Error processing data: {e}")
    ser.close()


if __name__ == "__main__":
    udp_server()
