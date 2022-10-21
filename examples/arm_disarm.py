from pymavlink import mavutil
from time import sleep

# Start connection on UDP port
eis = mavutil.mavlink_connection('udp:127.0.0.1:14444')

# Send arm/disarm command to FC
def send_cmd(i, arm):
        eis.mav.command_long_send(
            5,
            1,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            i, # confirmation
            arm,
            0,
            0,
            0,
            0,
            0,
            0)

# Get command acknowledgement from FC
def get_result():
    msg = eis.recv_match(type='COMMAND_ACK', blocking=False)
    if not msg:
        return -1
    if msg.get_type() == "BAD_DATA":
        if mavutil.all_printable(msg.data):
            sys.stdout.write(msg.data)
            sys.stdout.flush()
        return -1
    else:
        #Message is valid
        # Use the attribute
        print('Received command: %s' % msg.command)
        return msg.result

# Arm/disarm the vehicle
def arm_disarm(arm=0):
    i = 0
    while i < 255:
        send_cmd(i, arm)
        sleep(.05)
        res = get_result()
        if res != -1:
            print('Command result: %s' % res)
            break
        i = i+1
    if i == 255:
        return False
    return True


# Control loop
while True:
    try:
        print("Arming vehicle...")
        if not arm_disarm(1):
            print("Error sending command")#\nExiting...")
            sleep(2)#exit()
        else:
            sleep(10)

        print("Disarming vehicle...")
        if not arm_disarm(0):
            print("Error sending command")#\nExiting...")
            sleep(2)#exit()
        else:
            sleep(10)

    except KeyboardInterrupt:
        print("Exiting...")
        exit()