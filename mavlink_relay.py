from pymavlink import mavutil
import socketio
import time


# MAVLINK_HOST = 'udpin:127.0.0.1:5760' # Serial Port / QGC Relay
MAVLINK_HOST = 'tcp:127.0.0.1:5760' # SITL
MESSAGE_FREQUENCY = 2 # Number of seconds before each message poll
MAVLINK_CONNECTION_TIMEOUT = 2 # Try to reconnect after this many failed message polls

RELEVANT_MESSAGES = [
   'ARDUINO_SENSE',
   'HEARTBEAT',
   'GLOBAL_POSITION_INT',
   'GPS_STATUS',
   'SYS_STATUS',
   'RADIO_STATUS'
]

def connect_mavlink():
   mavlink = mavutil.mavlink_connection(MAVLINK_HOST)
   print("Waiting for heartbeat...")
   mavlink.wait_heartbeat()
   print("Heartbeat received: (system %u component %u)" % (mavlink.target_system, mavlink.target_component))
   return mavlink

def connect_sio():
   # TCP Relay Server
   SOCKET_URL="http://localhost:5001"
   sio = socketio.Client()
   print(f"\nConnecting to Socket: {SOCKET_URL}")
   sio.connect(SOCKET_URL)
   print("Socket Connected")
   return sio

def to_dict(msg):
    print(msg.get_type())
    for message_type in RELEVANT_MESSAGES:
        if msg.get_type() == message_type: # Check if the message type is relevant
            message_dict = {message_type: {}} # Create message dictionary
            message_dict['identity'] = { 'system': mavlink.target_system, 'component': mavlink.target_component }

            for field in msg.fieldnames:
                try:
                    message_dict[message_type][field] = getattr(msg, field)
                except:
                     return False
            return message_dict
    return False

def listen(mavlink):
   silence = 0
   while True:
      try:
         # Get message and error check
         msg = mavlink.recv_match();
         if msg is not None:   
            silence = 0             
            # Convert message to dictionary and relay it
            msg_dict = to_dict(msg)
            if msg_dict:
               print(f'Relaying msg: {msg.get_type()}')
               sio.emit("mavlink_data", msg_dict)
         else:
            # No messages. Try again soon
            time.sleep(MESSAGE_FREQUENCY)
            silence += 1
            if(silence >= MAVLINK_CONNECTION_TIMEOUT):
               silence = 0
               print("Attempting to reconnect to vehicle...")
               mavlink = connect_mavlink()

      except Exception as e:
         print("Exception: ", e)
         # Something went wrong. Try again soon
         time.sleep(MESSAGE_FREQUENCY)


mavlink = connect_mavlink()
sio = connect_sio()
listen(mavlink)
