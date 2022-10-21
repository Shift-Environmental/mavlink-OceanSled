from pymavlink import mavutil

# Start listening to UDP port
gcs = mavutil.mavlink_connection('udp:127.0.0.1:14555')

def get_msg():
    msg = gcs.recv_match(type='ARDUINO_SENSE', blocking=True, timeout=2)
    if not msg:
        return 0
    if msg.get_type() == "BAD_DATA":
        if mavutil.all_printable(msg.data):
            sys.stdout.write(msg.data)
            sys.stdout.flush()
        return -1
    else:
        #Message is valid
        # Use the attribute
        print(f'System ID: {gcs.target_system}')
        print(f'Time: {msg.time_boot_ms}')
        print(f'Leak: {msg.leak}')
        print(f'Temp: {round(msg.temp, 2)}')
        print(f'Humid: {round(msg.humid, 2)}')
        print(f'PPM: {round(msg.ppm, 2)}\n')
        return 1


# Control loop 
while True:
    try:
        if get_msg() == 0:
            print("No message received\nExiting...")
            exit()
        elif get_msg() == -1:
            print("Error receiving message\nExiting...")
            exit()
    except KeyboardInterrupt:
        print("Exiting...")
        exit()