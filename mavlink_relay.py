from pymavlink import mavutil
import socketio

# Start listening to serial port
com = mavutil.mavlink_connection('udpin:localhost:1234')

# TCP Relay Server
SOCKET_URL="http://localhost:5000"
sio = socketio.Client()
print(f"\nConnecting to Socket: {SOCKET_URL}")
sio.connect(SOCKET_URL)
print("Connected")

# Message types to relay (mavlink.io/en/messages/)
message_types = [
    'ARDUINO_SENSE',
    'HEARTBEAT',
    'GLOBAL_POSITION_INT',
    'GPS_STATUS',
    'SYS_STATUS',
    'RADIO_STATUS'
    ]

def to_dict(msg):
    for name in message_types:
        if msg.get_type() == name: # Check if the message type is wanted
            message_dict = {name: {}} # Create message dictionary

            for field in msg.fieldnames:
                try:
                    message_dict[name][field] = getattr(msg, field)
                except:
                    return False
            return message_dict
    return False


while True:
    try:
        # Get message and error check
        msg = com.recv_match();
        if msg is not None:                
            # Convert message to dictionary and relay it
            msg_dict = to_dict(msg)
            if msg_dict:
                print(f'Relaying msg: {msg.get_type()}')
                sio.emit("mavlink_data", msg_dict)

    except KeyboardInterrupt:
        print("Exiting...")
        exit()
