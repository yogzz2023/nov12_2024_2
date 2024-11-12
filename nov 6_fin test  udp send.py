import socket
import csv
import time
import numpy as np
import math

def sph2cart(az, el, r):
    x = r * np.cos(el * np.pi / 180) * np.sin(az * np.pi / 180)
    y = r * np.cos(el * np.pi / 180) * np.cos(az * np.pi / 180)
    z = r * np.sin(el * np.pi / 180)
    return x, y, z

def read_measurements_from_csv(file_path):
    measurements = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header if exists
        for row in reader:
            mr = float(row[10])  # MR column
            ma = float(row[11])  # MA column
            me = float(row[12])  # ME column
            mt = float(row[13])  # MT column
            md = float(row[14])
            x, y, z = sph2cart(ma, me, mr)  # Convert spherical to Cartesian coordinates
            print(f"Converted spherical to Cartesian: azimuth={ma}, elevation={me}, range={mr} -> x={x}, y={y}, z={z}")
            measurements.append((mr, ma, me, mt, md, x, y, z))
    return measurements

def form_measurement_groups(measurements, max_time_diff=0.050):
    measurement_groups = []
    current_group = []
    base_time = measurements[0][3]

    for measurement in measurements:
        if measurement[3] - base_time <= max_time_diff:
            current_group.append(measurement)
        else:
            measurement_groups.append(current_group)
            current_group = [measurement]
            base_time = measurement[3]

    if current_group:
        measurement_groups.append(current_group)

    return measurement_groups

def udp_sender(ip='127.0.0.1', port=5005, file_path='ttk.csv'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    measurements = read_measurements_from_csv(file_path)
    measurement_groups = form_measurement_groups(measurements, max_time_diff=0.050)
    
    for group in measurement_groups:
        message = ','.join(map(str, group))
        sock.sendto(message.encode('utf-8'), (ip, port))
        print(f"Sent message: {message}")
        time.sleep(1)  # Send a message every second

if __name__ == "__main__":
    udp_sender()
