from pymavlink import mavutil

# Start listening to UDP port
com = mavutil.mavlink_connection('udp:localhost:1234')

def get_msg():
    msg = com.recv_match(type='HEARTBEAT', blocking=True, timeout=2)
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
        return msg


# Control loop 
while True:
    try:
        msg = get_msg()
        if msg == 0:
            print("No message received\n")
        elif get_msg() == -1:
            print("Error receiving message\n")
        else:
            print(f'Got {msg.get_type()} from id {com.target_system}')
    except KeyboardInterrupt:
        print("Exiting...")
        exit()