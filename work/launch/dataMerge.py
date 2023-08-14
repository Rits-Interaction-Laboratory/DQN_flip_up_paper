import rospy
import message_filters
import keras
import pandas as pd
from dynamixel_msgs.msg import SensorState
from dynamixel_msgs.msg import MotorPWM
from dynamixel_msgs.msg import dataFrame
from dynamixel_msgs.msg import stateData
from std_msgs.msg import String
dataList = stateData()
lastState = stateData()
action = 0
lastAction = 0
startMark = 0
endDataFrame = dataFrame()
flag = 0
endMark = 0

def callback(pwmData, sensorData):
    global dataList, lastState, action, lastAction, endMark
    lastState = dataList
    lastAction = action
    dataList.distance = sensorData.distance
    dataList.x = sensorData.x
    dataList.y = sensorData.y
    dataList.MotorPWM = pwmData.MotorPWM
    dataList.Position = pwmData.Position
    action = pwmData.action
    if sensorData.distance <= 5.8 :
        endMark = 1
    if endMark == 1 :
        dataList.distance = 5.8

def keyboardCallback(data) :
    global endDataFrame, flag, startMark, lastState, lastAction, endMark
    if data.data == 'w' :
        startMark = 1
        endMark = 0
    elif data.data == 's' :
        startMark = 0
        endDataFrame.s = lastState
        endDataFrame.a = lastAction
        endDataFrame.newS = lastState
        flag = 1

if __name__ == '__main__':
    rospy.init_node('dataMerge', anonymous=True)
    rospy.Subscriber('/keyboardInput', String, keyboardCallback)
    sensorSub = message_filters.Subscriber('/sensorData', SensorState)
    pwmSub = message_filters.Subscriber('/PWM', MotorPWM)
    mergedDataPub = rospy.Publisher('dataFrame', dataFrame, queue_size=10) 
    plotDataPub = rospy.Publisher('plotFrame', stateData, queue_size=10)
    sync = message_filters.ApproximateTimeSynchronizer([pwmSub, sensorSub], 5, 0.01)
    sync.registerCallback(callback)
    while(True) :
        if startMark == 1 :
            dataPass = dataFrame()
            dataPass.s = lastState
            dataPass.a = lastAction
            dataPass.r = 0
            dataPass.newS = dataList
            mergedDataPub.publish(dataPass)
            plotData = stateData()
            plotData.x = dataList.x * 5
            plotData.y = dataList.y * 5
            plotData.distance = (dataList.distance - 5) * 20
            plotData.MotorPWM = action * 10
            plotData.Position = int(dataList.Position / 100)
            plotDataPub.publish(plotData)
        if flag == 1 :
           print("please input reward and reset robot:")
           inputReward = input()
           endDataFrame.r = int(inputReward)
           mergedDataPub.publish(endDataFrame)
           dataList = stateData()
           lastState = stateData()
           action = 0
           lastAction = 0
           startMark = 0
           endDataFrame = dataFrame()
           flag = 0   
        rospy.sleep(0.01)
