from pymavlink import mavutil
from time import sleep

# Start listening to serial port
com = mavutil.mavlink_connection('udpin:localhost:1234')


last = 0
while True:
    com.recv_match(type='ARDUINO_SENSE', blocking=False) # Look for new messages asynchronously
    try:
        msg = com.messages['ARDUINO_SENSE'] # Last received message
        #if com.time_since('ARDUINO_SENSE') == 0: # Print every new message
        if last is not msg.time_boot_ms: # Print every unique message
            print(f'New message from system #{com.target_system}:')
            print(f'{msg.get_type()} [{msg.time_boot_ms}]: {msg.status}, {msg.pan}, {msg.tilt}\n')
            last = msg.time_boot_ms
            sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        exit()
    except:
        sleep(1)