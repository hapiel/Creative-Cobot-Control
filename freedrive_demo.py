import rtde_control
import rtde_receive
import time
rtde_c = rtde_control.RTDEControlInterface("192.168.12.1")
rtde_r = rtde_receive.RTDEReceiveInterface("192.168.12.1")

while True:
    try:
        print("next round")
        rtde_c.moveJ([0, -1, 0, -0, 0, 0], 1.8, 2.1)
        tcp_force = rtde_r.getActualTCPForce()
        force_sum = sum(abs(tcp_force[i]) for i in range(6))
        while force_sum > 1500:
            time.sleep(0.1)
            tcp_force = rtde_r.getActualTCPForce()
            force_sum = sum(abs(tcp_force[i]) for i in range(6))
            print(f"Sum of absolute forces: {force_sum}")

        rtde_c.teachMode()
        time.sleep(2)
        tcp_speed = rtde_r.getActualTCPSpeed()
        speed_sum = sum(abs(tcp_speed[i]) for i in range(6))
        while speed_sum > 0.1:
            time.sleep(0.1)
            tcp_speed = rtde_r.getActualTCPSpeed()
            # print(tcp_speed)
            speed_sum = sum(abs(tcp_speed[i]) for i in range(6))
        rtde_c.endTeachMode()
    except Exception as e:
        print(f"An error occurred: {e}")
