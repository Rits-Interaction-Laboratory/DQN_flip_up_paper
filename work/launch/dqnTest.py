import torch                                    
import torch.nn as nn                           
import torch.nn.functional as F                 
import numpy as np                 
import pandas as pd
import os
import rospy            
from dynamixel_msgs.msg import dataFrame
from dynamixel_msgs.msg import stateData
from std_msgs.msg import String, Int32

BATCH_SIZE = 32                                 
LR = 0.01                                       
EPSILON = 0.9                                   
GAMMA = 0.9                                     
TARGET_REPLACE_ITER = 10                       
MEMORY_CAPACITY = 2000                         
N_ACTIONS = 10                               
N_STATES = 4                              
startMark = 0
model_dir = '/home/jubileus/motor/src/dynamixel_motor/model/4'
runningLoss = []

class Net(nn.Module):
    def __init__(self):                                                         
        super(Net, self).__init__()                                             
        self.fc1 = nn.Linear(N_STATES, 50)                                      
        self.fc1.weight.data.normal_(0, 0.1)                                    
        self.out = nn.Linear(50, N_ACTIONS)                                     
        self.out.weight.data.normal_(0, 0.1)                                    

    def forward(self, x):                                                       
        x = F.relu(self.fc1(x))                                                 
        actions_value = self.out(x)                                             
        return actions_value        

class DQN(object):
    def __init__(self):                                                         
        self.eval_net, self.target_net = Net(), Net()  
        self.target_net.load_state_dict(torch.load(model_dir + "/model_100.pth"))   
        self.eval_net.load_state_dict(torch.load(model_dir + "/model_100.pth"))
        self.eval_net.eval()                      
        self.learn_step_counter = 0                                             
        self.memory_counter = 0                                                 
        self.memory = np.zeros((MEMORY_CAPACITY, N_STATES * 2 + 2))            
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=LR)    
        self.loss_func = nn.MSELoss()                                           

    def choose_action(self, x):                                                 
        x = torch.unsqueeze(torch.FloatTensor(x), 0)                                                                 
        actions_value = self.eval_net.forward(x)                            
        action = torch.max(actions_value, 1)[1].data.numpy()                
        action = action[0]                                                                            
        return action                                                                                               

dqn = DQN()
rospy.init_node('DQN', anonymous=True)
pub = rospy.Publisher('action', Int32, queue_size=10) 

def keyboardCallback(data) :
    global startMark
    if data.data == 's':
        startMark = 1
    if data.data == 'w':
        startMark = 0

def callback(data) :
    global dqn, pub, startMark
    maxDistance = 8.0
    s = [data.s.distance, data.s.x, data.s.y, data.s.MotorPWM]
    print(s)
    a = dqn.choose_action(s)                                       
    pub.publish(a)            

if __name__ == '__main__':
    rospy.Subscriber('/dataFrame', dataFrame, callback)
    rospy.Subscriber('/keyboardInput', String, keyboardCallback)
    k = 0
    rospy.spin()
