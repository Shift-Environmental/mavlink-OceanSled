from pymavlink import mavutil
from time import sleep
import socketio

# Start listening to serial port
com = mavutil.mavlink_connection('COM14')

# TCP Relay Server
SOCKET_URL="http://localhost:5000"
sio = socketio.Client()
print(f"\nConnecting to Socket: {SOCKET_URL}")
sio.connect(SOCKET_URL)
print("Connected")


message_types = [
    'HEARTBEAT',
    'GLOBAL_POSITION_INT',
    'ARDUINO_SENSE'
    ]

# Parse message_types messages into dictionary
def get_data(name):
    msg = com.recv_match(type=name, blocking=False) # Look for new messages
    if not msg:
        return False
    if msg.get_type() == "BAD_DATA":
        if mavutil.all_printable(msg.data):
            sys.stdout.write(msg.data)
            sys.stdout.flush()
        return False
    
    message_dict = {name: {}} # Create message dictionary


    for field in msg.fieldnames:
        try:
            message_dict[name][field] = getattr(msg, field)
        except:
            return False
            break
    return message_dict
            
           

while True:
    try:
        for name in message_types:
            mavlink_data = get_data(name)
            if not mavlink_data:
                print(f'Error parsing message: {name}')
            else:
                print(f'Relaying msg: {name}')
                sio.emit("mavlink_data", mavlink_data)

    except KeyboardInterrupt:
        print("Exiting...")
        exit()

exit()
