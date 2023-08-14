import rospy
import sys
import tty
import time
import termios
from std_msgs.msg import String 
def callback(data):
    current_state = data
    for motor_state in data.motor_states :
        print(motor_state)

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)

if __name__ == '__main__':
    rospy.init_node('teleop',anonymous=True)
    pub = rospy.Publisher('keyboardInput', String, queue_size=10) 
    data = "";
    while(data != 'q'):
        data = readkey()
        pub.publish(data)   
    
