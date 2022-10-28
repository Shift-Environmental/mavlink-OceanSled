from pymavlink import mavutil
from time import sleep
import socket
import json

# Start listening to serial port
com = mavutil.mavlink_connection('udp:127.0.0.1:14555')

# UDP Relay Server
UDP_IP = "127.0.0.1"
UDP_PORT = 5000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Wait for sensor data
def get_data():
    msg = com.recv_match(type='ARDUINO_SENSE', blocking=True, timeout=2)
    if not msg:
        return False
    if msg.get_type() == "BAD_DATA":
        if mavutil.all_printable(msg.data):
            sys.stdout.write(msg.data)
            sys.stdout.flush()
        return False
    else:
        #Message is valid
        return msg

while True:
    try:
        msg = get_data()
        if not msg:
            print('Error receiving message')
            sleep(1)
        else:
            json_string = json.dumps({
                'type': 'telemetry',
                'data': {
                   'msg_type': msg.get_type(),
                   'sys_id': com.sysid,
                   'leak': msg.leak,
                   'temp': msg.temp,
                   'humid': msg.humid,
                   'ppm': msg.ppm
                }
            })
            sock.sendto(bytes(json_string, "utf-8"), (UDP_IP, UDP_PORT))
         
            print(json_string)
    except KeyboardInterrupt:
        print("Exiting...")
        exit()




# Test w/ Dummy Data
#
# json_test_string = json.dumps({
#     'type': 'telemetry',
#     'data': {
#        'sys_id': com.sysid,
#        'leak': False,
#        'temp': 14.2274,
#        'humid': 57.3381,
#        'ppm': 1564.23287
#     }
# })
#
# while True:
#     try:
#         sock.sendto(bytes(json_test_string, "utf-8"), (UDP_IP, UDP_PORT))
#         sleep(1)
#     except KeyboardInterrupt:
#         print("Exiting...")
#         exit()