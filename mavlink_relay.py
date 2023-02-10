import argparse
from pymavlink import mavutil
import socketio
import time

parser = argparse.ArgumentParser(description='Command Line Arguments')
parser.add_argument('--host', default='sled', help='Mavlink Host: sled (default) | sim')
args = parser.parse_args()

if args.host == 'sim':
   MAVLINK_HOST = 'tcp:127.0.0.1:5760' # SITL
else:
   MAVLINK_HOST = 'udpin:127.0.0.1:5760' # Serial Port / QGC Relay

MAVLINK_HOST = 'udpin:127.0.0.1:1234' # Serial Port / QGC Relay
# MAVLINK_HOST = 'tcp:127.0.0.1:5760' # SITL
MESSAGE_FREQUENCY = 0.5 # Number of seconds before each message poll
MAVLINK_CONNECTION_TIMEOUT = 10 # Try to reconnect after this many failed message polls
SOCKET_URL="http://localhost:8001"

RELEVANT_MESSAGES = [
   'ARDUINO_SENSE',
   'HEARTBEAT',
   'GLOBAL_POSITION_INT',
   'ATTITUDE',
   "BATTERY_STATUS",
   "DISTANCE_SENSOR",
   "VFR_HUD"
]

def connect_mavlink():
   mavlink = mavutil.mavlink_connection(MAVLINK_HOST)
   print("Waiting for heartbeat...")
   mavlink.wait_heartbeat()
   print("Heartbeat received: (system %u component %u)" % (mavlink.target_system, mavlink.target_component))
   return mavlink

def connect_sio():
   # TCP Relay Server
   sio = socketio.Client()
   print(f"\nConnecting to Socket: {SOCKET_URL}")
   sio.connect(SOCKET_URL)
   print("Socket Connected")
   return sio

def to_dict(msg):
    print(msg.get_type())
    for msg_type in RELEVANT_MESSAGES:
        if msg.get_type() == msg_type: # Check if the message type is relevant
            # Create message dictionary
            message_dict = {
               'system_id': mavlink.target_system,
               #'component_id': mavlink.target_component,
               'msg_type': msg_type,
               'data': {}}

            for field in msg.fieldnames:
               try:
                  message_dict['data'][field] = getattr(msg, field)
               except:
                  return False
            return message_dict
    return False


def listen(mavlink):
   relayed_messages = {}
   while True:
      try:
         # Get message and error check
         msg = mavlink.recv_match();

         # LIMIT MESSAGES TO 1 PER TIC
         if(msg.get_type() not in relayed_messages):
            relayed_messages[msg.get_type()] = True
         else: # MESSAGE ALREADY SENT THIS TIC
            continue

         if msg is not None:
            silence = 0
            # Convert message to dictionary and relay it
            msg_dict = to_dict(msg)
            if msg_dict:
               print(f'Relaying msg: {msg.get_type()}')
               sio.emit("mavlink_data", msg_dict)
         else:
            # No messages. Try again soon
            relayed_messages = {} #CLEAR SENT MESSAGES
            time.sleep(MESSAGE_FREQUENCY)
            silence += 1
            if(silence >= MAVLINK_CONNECTION_TIMEOUT):
               silence = 0
               print("Attempting to reconnect to vehicle...")
               mavlink = connect_mavlink()

      except Exception as e:
         relayed_messages = {} #CLEAR SENT MESSAGES
         print("Exception: ", e)
         # Something went wrong. Try again soon
         time.sleep(MESSAGE_FREQUENCY)


mavlink = connect_mavlink()
sio = connect_sio()
listen(mavlink)
