from dynamixel_msgs.msg import MotorState
from dynamixel_msgs.msg import MotorStateList
import rospy

def callback(data):
    current_state = data
    for motor_state in data.motor_states :
        print(motor_state)

if __name__ == '__main__':
    current_state = MotorStateList()
    rospy.init_node('listener', anonymous=True)
    rospy.Subscriber('/motor_states/pan_tilt_port/', MotorStateList, callback)
    print("I'm a checkpoint!")
    rospy.spin()
    
