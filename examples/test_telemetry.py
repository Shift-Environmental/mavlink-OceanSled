from pymavlink import mavutil
from time import sleep

# Start connection on UDP port
port = mavutil.mavlink_connection('udp:127.0.0.1:14555')

def send_data(i):
    port.mav.heartbeat_send(
        11,
        3,
        64,
        0,
        3,
        i)

    port.mav.arduino_sense_send(
        i,  # timestamp
        0,  # leak
        20.1,  # temp
        56.2,  # humidity
        0.0,  # tvoc
        256.3,  # pan angle
        45.4,  # tilt angle
        0)  # status


# Control loop
i = 1
while True:
    try:
        print(f"Sending packet #{i}")
        if not send_data(i):
            print("Error sending packet.")
        i = i+1
        sleep(2)

    except KeyboardInterrupt:
        print("Exiting...")
        exit()