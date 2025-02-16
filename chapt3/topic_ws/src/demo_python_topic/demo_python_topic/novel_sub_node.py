import rclpy
from rclpy.node import Node
from example_interfaces.msg import String
import threading
from queue import Queue
import time
import subprocess


class NovelSubNode(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        self.novels_queue_ = Queue()
        self.novel_subscriber_ = self.create_subscription(
            String, 'novel', self.novel_callback, 10)
        self.speech_thread_ = threading.Thread(target=self.speak_thread)
        self.speech_thread_.start()

    def novel_callback(self, msg):
        self.novels_queue_.put(msg.data)

    def speak_thread(self):
        while rclpy.ok():
            if self.novels_queue_.qsize() > 0:
                text = self.novels_queue_.get()
                self.get_logger().info(f'正在朗读: {text}')
                # 使用 subprocess.Popen 异步调用 espeak-ng
                subprocess.Popen(["espeak-ng", "-v", "zh", text])
            else:
                time.sleep(0.1)  # 减少 sleep 时间，避免延迟


def main(args=None):
    rclpy.init(args=args)
    node = NovelSubNode("novel_read")
    rclpy.spin(node)
    node.speech_thread_.join()  # 等待线程结束
    rclpy.shutdown()
