from optparse import OptionParser
from dynamixel_msgs.msg import MotorPWM
from dynamixel_msgs.msg import MotorState
from dynamixel_msgs.msg import MotorStateList
from std_msgs.msg import String, Int32
from threading import Thread, Lock
import rospy
import time
import roslib
import sys
import tty
import termios
import numpy as np
roslib.load_manifest('dynamixel_driver')

from dynamixel_driver import dynamixel_io
from std_msgs.msg import String, Float64
Str = ""
Goal = -1
Speed = 20
Id = 37
Key = ''
startMark = 0
targetSpeed = 0

def callback(data):
    global Str, Goal, Speed, Key, startMark
    Key = data.data
    print (Key, time.time())
    if Key == 'w' :
        startMark = 1
    if Key == 's' :
        startMark = 0
    if Key == 'r' :
        Goal, Speed = Stop(Goal, Speed)

def speedCallBack(data) :
    global targetSpeed, startMark
    if startMark == 1 :
        targetSpeed = data.data * 5
    else :
        targetSpeed = 0

def movef(Goal, Speed) :
    if Goal == -1 or Goal <= present_pos:
        Speed = 20
        Goal = 3040
    if Goal > present_pos:
        Speed += 5
        if Goal != 3040 :
            Goal = 3040
    return Goal, Speed

def moveb(Goal, Speed) :
    present_pos = dxl_io.get_position(Id)
    if Goal == -1 or Goal >= present_pos:
        Speed = -20
        Goal = 10
    if Goal < present_pos:
        Speed -= 5
        if Goal != 10 :
    	    Goal = 10
    return Goal, Speed

def Stop(Goal, Speed) :
    Speed = 0
    return Goal, Speed

def speed2Distance(targetSpeed) :
    return targetSpeed * 2    

def pwm2Distance(targetPwm) :
    return targetPwm * 5.66

if __name__ == '__main__':
    parser = OptionParser(usage='Usage: %prog [options]')
    parser.add_option('-p', '--port', metavar='PORT', default='/dev/ttyUSB0')
    parser.add_option('-b', '--baud', metavar='BAUD', type="int", default=1000000)
    rospy.init_node('mainCtrl', anonymous=True)
    current_state = MotorPWM()
    pub = rospy.Publisher('PWM', MotorPWM, queue_size=10) 
    rospy.Subscriber('/keyboardInput', String, callback)
    rospy.Subscriber('/action', Int32, speedCallBack)
    rate = rospy.Rate(100) 
    (options, args) = parser.parse_args(sys.argv)
    port = options.port
    baudrate = options.baud
    
    Id = 37
    flag = 0
    last_pos = 0
    Time = 0;
    key = ''
    keyFlag = 0
    k = 1.0
    x = 0.0
    maxSpeed = 255
    constParameter = 0.5

    try:
        dxl_io = dynamixel_io.DynamixelIO(port, baudrate)
    except dynamixel_io.SerialOpenError as soe:
        print ('ERROR:', soe)
    else:
        dxl_io.set_speed(37, 0)
        dxl_io.set_p_gain(37, 8)
        dxl_io.set_position(39, 0)
        Time = time.time()
        while(flag != 1):
            #targetSpeed = maxSpeed * np.sin(k * x * 3.1415926)
            present_pos = dxl_io.get_position(Id)
            present_speed = dxl_io.get_speed(Id)
            pwm = dxl_io.get_motor_pwm(Id) - 256
            if pwm <= 0:
                pwm = -256 - pwm
            current_state.Position = present_pos
            current_state.Speed = present_speed * -1
            current_state.MotorPWM = pwm
            current_state.calc_Speed = targetSpeed
            current_state.header.stamp = rospy.Time.now()
            current_state.action = targetSpeed / 5
            pub.publish(current_state)
            print(targetSpeed, startMark)
            if startMark == 0 :
                dxl_io.set_position(37, int(0))
            else : 
                if targetSpeed > 0 :
                    Goal = 3040
                elif targetSpeed < 0 :
                    Goal = 0
                elif targetSpeed == 0:
                    Goal = present_pos
                if targetSpeed != 0 :
                    frontDistance = (targetSpeed - pwm) * constParameter + pwm2Distance(targetSpeed)
                if Goal != -1 and Goal < present_pos:
                    dxl_io.set_position(37, int(max(Goal, present_pos + frontDistance)))
	  	#dxl_io.set_position(39, int(max(Goal, present_pos + frontDistance)))
                #print(Goal, int(max(Goal, present_pos - frontDistance)), present_pos)
                elif Goal > present_pos:
                    dxl_io.set_position(37, int(min(Goal, present_pos + frontDistance)))
                #print(Goal, int(min(Goal, present_pos + frontDistance)), present_pos)
		#dxl_io.set_position(39, int(max(Goal, present_pos + frontDistance)))
            #if Key == 'c' :
            #    startMark = 1
            if Key == 'q' :
                flag = 1
            Key = ''
            #if startMark == 1 :
            #    x += 0.9
    #rospy.spin()
            
