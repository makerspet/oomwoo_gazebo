import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSReliabilityPolicy

class StringSaver(Node):
    def __init__(self):
        super().__init__('string_saver')
        latched_qos = QoSProfile(
            depth=1,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            reliability=QoSReliabilityPolicy.RELIABLE
        )
        self.subscription = self.create_subscription(
            String,
            'robot_description',  # Replace with your topic name
            self.listener_callback,
            latched_qos)
        self.subscription  # prevent unused variable warning
        self.file_path = 'saved_strings.txt' # Define your output file path

        # Open the file in append mode. 'a' creates the file if it doesn't exist.
        self.file = open(self.file_path, 'a')
        self.get_logger().info(f'Saving strings to: {self.file_path}')

    def listener_callback(self, msg):
        self.get_logger().info(f'Received: "{msg.data}"')
        self.file.write(msg.data + '\n') # Write the string and a newline character
        self.file.flush() # Ensure data is written to disk immediately

    def destroy_node(self):
        self.file.close() # Close the file when the node is destroyed
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    string_saver = StringSaver()
    try:
        rclpy.spin(string_saver)
    except KeyboardInterrupt:
        pass
    finally:
        string_saver.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
