import serial
import rospy
import time
from dynamixel_msgs.msg import SensorState


def feedback() :
    while not rospy.is_shutdown():
    	data = port.readline()
    	data.decode()
    	dis, x, y = data.split(' ');
    	distance = float(dis)
    	mvX = int(x)
    	mvY = int(y[0:-2])
    	sensorData = SensorState()
    	sensorData.distance = distance
    	sensorData.x = mvX
    	sensorData.y = mvY
    	sensorData.header.stamp = rospy.Time.now()
    	pub.publish(sensorData)

if __name__ == '__main__':
    
    port = serial.Serial('/dev/ttyACM0', 9600)
    rospy.init_node('sensor',anonymous=True)
    pub = rospy.Publisher('sensorData', SensorState, queue_size=10) 
    try:
        feedback()
    except rospy.ROSInterruptException:
        print("Stop")

        
