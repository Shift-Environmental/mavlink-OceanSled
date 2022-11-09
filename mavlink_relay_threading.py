from pymavlink import mavutil
from time import sleep
import threading
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


# Thread for waiting on individual messages
class RelayThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self): # Transmit message to relay server
        try:
            mavlink_data = getData(self.name)
            if not mavlink_data:
                print(f'Error parsing message: {self.name}')
                return
            else:
                print(f'Relaying msg: {self.name}')
                sio.emit("mavlink_data", mavlink_data)
        except KeyboardInterrupt:
            print("Exiting...")
            exit()
        except:
            return
            
# Parse messages into dictionary
def getData(name):
    msg = com.recv_match(type=name, blocking=True, timeout=10) # Look for new messages
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

                       
def main():
    try:
        while True:
            for message in message_types:
                threads = threading.enumerate()
                exists = False
                    
                for t in threads: # Check if this thread already exists
                    if t.name == message:
                        exists = True
    
                if not exists: # Create new thread for message if it doesn't exist
                    #print(f'Creating thread: {message}')
                    newThread = RelayThread(message_types.index(message), message)
                    newThread.start()

    except KeyboardInterrupt:
        print("Exiting...")
        exit()


# Call main
main()
