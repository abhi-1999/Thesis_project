#!/usr/bin/env python3
import time
import psutil
import rclpy
from std_msgs.msg import Float32
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy


class Computation:
    def __init__(self):
        self.target = 30
        self.kp = 2.5   #2.5
        self.kd = 0.015  #0.01
        self.ki = 0.4   #0.2
        self.eprev = 0
        self.eintegral = 0
        self.prevT = 0
        self.prevPosition_L = 0
        self.packets_sent_start = psutil.net_io_counters().packets_sent
        self.packets_recv_start = psutil.net_io_counters().packets_recv

    
    def get_system_info(self):
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        net_io = psutil.net_io_counters()
        temp = None
        packets_sent = net_io.packets_sent - self.packets_sent_start 
        packets_recv = net_io.packets_recv - self.packets_recv_start



        if hasattr(psutil, "sensors_temperatures"):                
            temperatures = psutil.sensors_temperatures() 
            if "coretemp" in temperatures:
                  temp = temperatures["coretemp"][0].current
        
        return cpu_usage, memory_usage, temp, packets_sent, packets_recv
    
    def control_logic(self, current_position_L):
        t = time.time()
        
        deltaT = t - self.prevT
        velocity = (current_position_L - self.prevPosition_L) / deltaT   # count/s
        self.prevPosition_L = current_position_L
        self.prevT = t

        # Convert count/s to rpm
        v = (velocity / 12532) * 60

        e = self.target - v
        self.eintegral = self.eintegral + e * deltaT
        ederivative = (e - self.eprev) / deltaT

        u = self.kp * e + self.ki * self.eintegral + self.kd * ederivative  
        self.eprev = e

        return u


class MyNode(Node):
    def __init__(self):
        super().__init__("PC_node")
        
        self.glob_time = time.time()
        self.counter = 0
        qos_policy = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.cmd_ctrl_pub = self.create_publisher(Float32, "micro_ros_esp_sub", 1)
        self.subscription = self.create_subscription(Float32, "micro_ros_esp_pub", self.listener_callback, qos_profile=qos_policy)

        self.get_logger().info("PC_node has started")

        first_pub = Float32()
        first_pub.data = 10.0
        self.cmd_ctrl_pub.publish(first_pub)
        print("sent first command")
        
    def listener_callback(self, msg):
        t = time.time()
        u = self.computation.control_logic(msg.data)
        

        cpu_usage, memory_usage, temperature, packets_sent, packets_recv = self.computation.get_system_info()
        time_stamp = time.time() - self.glob_time 

        print(f"Iteration: {self.counter}| Time stamp: {time_stamp}| CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage}% | CPU Temperature: {temperature} °C|Packets sent: {packets_sent}| Packets received: {packets_recv}")
        self.counter += 1

        new_msg = Float32()
        new_msg.data = u
        self.cmd_ctrl_pub.publish(new_msg)
        print(time.time() - t)


def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    node.computation = Computation()  # Initialize Computation class
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
