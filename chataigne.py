from pythonosc import dispatcher, udp_client
from pythonosc.osc_server import ThreadingOSCUDPServer
import rtde_control
import rtde_receive
import threading
import time
import math
import socket

ROBOT_IP = "192.168.12.1"
OSC_LISTEN_IP = "0.0.0.0"
OSC_LISTEN_PORT = 9000
# OSC_SEND_IP = "127.0.0.1"
OSC_SEND_IP = "192.168.12.255" # broadcast
OSC_SEND_PORT = 8000

# UR interfaces
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)

# OSC client (for sending data)
# client = udp_client.SimpleUDPClient(OSC_SEND_IP, OSC_SEND_PORT)

client = udp_client.SimpleUDPClient(OSC_SEND_IP, OSC_SEND_PORT)
client._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def deg_to_rad(deg):
    return deg * math.pi / 180.0

def rad_to_deg(rad):
    return rad * 180.0 / math.pi

# MoveJ handler
def handle_movej(unused_addr, *args):
    if len(args) not in [6, 8]:
        print("Expected 6 joint values (°), optionally followed by acceleration (°/s²) and speed (°/s).")
        return
    try:
        joint_positions = [deg_to_rad(j) for j in args[:6]]
        acceleration = deg_to_rad(args[6]) if len(args) > 6 else deg_to_rad(30.0)
        speed = deg_to_rad(args[7]) if len(args) > 7 else deg_to_rad(15.0)
        rtde_c.moveJ(joint_positions, acceleration, speed, True)
    except Exception as e:
        print(f"moveJ error: {e}")
        

def handle_movel(unused_addr, *args):
    if len(args) not in [6, 8]:
        print("Expected 6 pose values (x, y, z in m, rx, ry, rz in °), optionally followed by acceleration (m/s²) and speed (m/s).")
        return
    
    try:
        # Required pose
        # First three are position in meters, last three are orientation in degrees → convert to radians
        pose = list(args[:3]) + [deg_to_rad(val) for val in args[3:6]]

        # Optional parameters
        acceleration = args[6] if len(args) > 6 else 0.25   # [m/s²]
        speed = args[7] if len(args) > 7 else 0.25          # [m/s]

        # Send moveL command (blocking = True)
        rtde_c.moveL(pose, acceleration, speed, True)
        print(f"moveL executed: pose={pose}, a={acceleration}, v={speed}")

    except Exception as e:
        print(f"moveL error: {e}")


def handle_servoj(unused_addr, *args):
    if len(args) not in [6, 10]:
        print("Expected 6 joint values (deg), optionally followed by lookahead_time, gain, acceleration, and speed.")
        return
    try:
        joint_positions_deg = list(args[:6])
        joint_positions_rad = [math.radians(j) for j in joint_positions_deg]

        # Optional parameters
        lookahead_time = args[6] if len(args) > 6 else 0.1
        gain = args[7] if len(args) > 7 else 300
        acceleration = math.radians(args[8]) if len(args) > 8 else math.radians(100)
        speed = math.radians(args[9]) if len(args) > 9 else math.radians(100)

        rtde_c.servoJ(joint_positions_rad, acceleration, speed, 0.002, lookahead_time, gain)
    except Exception as e:
        print(f"servoj error: {e}")
        
def handle_servoj_stop(unused_addr):
    try:
        rtde_c.servoStop()
        print("ServoJ stopped.")
    except Exception as e:
        print(f"servoj_stop error: {e}")
        
    
def handle_servol(unused_addr, *args):
    if len(args) not in [6, 9]:
        print("Expected 6 pose values (x, y, z in m, rx, ry, rz in °), optionally followed by time, lookahead_time, and gain.")
        return
    try:
        # Required pose: convert last three (orientation) from degrees → radians
        pose = list(args[:3]) + [deg_to_rad(val) for val in args[3:6]]

        # Optional parameters
        time = args[6] if len(args) > 6 else 0.002  # [s] How long the command influences robot
        lookahead_time = args[7] if len(args) > 7 else 0.1
        gain = args[8] if len(args) > 8 else 300

        # speed and acceleration are not used in servoL
        rtde_c.servoL(pose, 0.0, 0.0, time, lookahead_time, gain)
        # print(f"servoL executed: pose={pose}, t={time}, lookahead={lookahead_time}, gain={gain}")

    except Exception as e:
        print(f"servol error: {e}")


def handle_servol_stop(unused_addr):
    try:
        rtde_c.servoStop()
        print("ServoL stopped.")
    except Exception as e:
        print(f"servol_stop error: {e}")


# Teach mode handler
def handle_teachmode(unused_addr, flag):
    try:
        if flag == 1:
            rtde_c.teachMode()
            print("Teach mode activated.")
        else:
            tcp_speed = rtde_r.getActualTCPSpeed()
            speed_sum = sum(abs(tcp_speed[i]) for i in range(6))
            while speed_sum > 0.1:
                # print(f"Current TCP speed: {tcp_speed}, waiting to end teach mode...")
                # time.sleep(0.1)
                tcp_speed = rtde_r.getActualTCPSpeed()
                # print(tcp_speed)
                speed_sum = sum(abs(tcp_speed[i]) for i in range(6))
            rtde_c.endTeachMode()
            print("Teach mode ended.")
    except Exception as e:
        print(f"Teach mode error: {e}")
        
def handle_stop(unused_addr):
    try:
        print("Stopping all motion...")

        decel = 10.0  # [rad/s^2] for speedJ / [m/s^2] for speedL / servo stop

        # Stop normal motions
        rtde_c.stopJ(500, True)               # joint stop
        # rtde_c.stopL(0.5)               # linear stop
        # rtde_c.speedStop(decel)        # stop speed motions with deceleration
        # rtde_c.jogStop()               # stop jog motions
        # rtde_c.forceModeStop()         # exit force mode

        # # Stop servo motions with deceleration
        # rtde_c.servoStop(decel)

        # # Stop any running URScript
        # rtde_c.stopScript()

        print("Robot stop command issued.")
    except Exception as e:
        print(f"Error stopping robot: {e}")

# Start OSC dispatcher
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/movej", handle_movej)
dispatcher.map("/movel", handle_movel)
dispatcher.map("/teach_mode", handle_teachmode)
dispatcher.map("/servoj", handle_servoj)
dispatcher.map("/servoj_stop", handle_servoj_stop)
dispatcher.map("/stop", handle_stop)
dispatcher.map("/servol", handle_servol)
dispatcher.map("/servol_stop", handle_servol_stop)



server = ThreadingOSCUDPServer((OSC_LISTEN_IP, OSC_LISTEN_PORT), dispatcher)

# Thread to periodically send joint states
if __name__ == "__main__":
    print(f"Listening for OSC on {OSC_LISTEN_IP}:{OSC_LISTEN_PORT}")

    # Start OSC server in the background
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    while True:
        try:
            joints = rtde_r.getActualQ()
            joint_values_deg = [rad_to_deg(j) for j in joints]
            client.send_message("/joints", joint_values_deg)

            # Send TCP force (6 components) in one message
            tcp_force = rtde_r.getActualTCPForce()
            client.send_message("/tcp_force", tcp_force)
            
            # joint_torque = rtde_c.getJointTorques()
            # client.send_message("/joint_torque", joint_torque)
            # DOESN"T WORK VERY WELL WITH TEACH MODE, FIXME

            # Send TCP pose (x, y, z in meters, rx, ry, rz in degrees)
            tcp_pose = rtde_r.getActualTCPPose()  # [x, y, z, rx, ry, rz]
            tcp_pose_converted = tcp_pose[:3] + [rad_to_deg(val) for val in tcp_pose[3:]]
            client.send_message("/tcp_pose", tcp_pose_converted)
            
            
        except Exception as e:
            print(f"Error in RTDE loop: {e}")

        time.sleep(0.03)  # 100Hz loop frequency, adjust as needed
        
        
        