from pymavlink import mavutil
from time import sleep

# Start listening to serial port
com = mavutil.mavlink_connection('udp:127.0.0.1:14555')


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

with open('pos.csv', 'w') as f:
    #f.write('Message_Type, System_ID, Latitude, Longitude, Altitude, Relative_Alt, Heading\n')
    while True:
        try:
            msg = get_data()
            if not msg:
                print('Error receiving message')
                sleep(1)
            else:
                print(f'{msg.get_type()}, {com.sysid}, {msg.time_boot_ms}, {msg.status}\n')
        except KeyboardInterrupt:
            print("Exiting...")
            exit()