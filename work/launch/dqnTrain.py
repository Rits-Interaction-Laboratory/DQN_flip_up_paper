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

BATCH_SIZE = 32      #random draft from pool                           
LR = 0.01            #learning rate                           
EPSILON = 0.9        #probability of random choose action                           
GAMMA = 0.9          #parameter in DQN                           
TARGET_REPLACE_ITER = 10  #update targenet net per 10 iter                     
MEMORY_CAPACITY = 6000    #max size of memory pool                     
N_ACTIONS = 10       #actions node                           
N_STATES = 4         #input node                      
startMark = 0
model_dir = '/home/jubileus/motor/src/dynamixel_motor/model/withoutPWM' #save dir
runningLoss = []
rewardMemory = []
startLearn = 0
startTime = 0

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
        #self.target_net.load_state_dict(torch.load(model_dir + "/model_50.pth"))   #load weight if need
        #self.eval_net.load_state_dict(torch.load(model_dir + "/model_50.pth"))                       
        self.learn_step_counter = 0                                             
        self.memory_counter = 0                                                 
        self.memory = np.zeros((MEMORY_CAPACITY, N_STATES * 2 + 2))            
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=LR)    
        self.loss_func = nn.MSELoss()                                           

    def choose_action(self, x):    #choose action and send it to mainCtrl                                             
        x = torch.unsqueeze(torch.FloatTensor(x), 0)                            
        if np.random.uniform() < EPSILON:                                       
            actions_value = self.eval_net.forward(x)                            
            action = torch.max(actions_value, 1)[1].data.numpy()                
            action = action[0]                                                  
        else:                                                                   
            action = np.random.randint(0, N_ACTIONS)                            
        return action                                                           

    def store_transition(self, s, a, r, s_):      #save data in pool                              
        transition = np.hstack((s, [a, r], s_))                                 
        index = self.memory_counter % MEMORY_CAPACITY                           
        self.memory[index, :] = transition                                      
        self.memory_counter += 1                                                

    def learn(self):        #DQN main learning
        global runningLoss                                                    
        if self.learn_step_counter % TARGET_REPLACE_ITER == 0:                  
            self.target_net.load_state_dict(self.eval_net.state_dict())  
            model_path = os.path.join(model_dir, "model_{}".format(self.learn_step_counter) +".pth")
            torch.save(self.eval_net.state_dict(), model_path)       
        self.learn_step_counter += 1                                            

        sample_index = np.random.choice(MEMORY_CAPACITY, BATCH_SIZE)            
        b_memory = self.memory[sample_index, :]                                 
        b_s = torch.FloatTensor(b_memory[:, :N_STATES])
        b_a = torch.LongTensor(b_memory[:, N_STATES:N_STATES+1].astype(int))
        b_r = torch.FloatTensor(b_memory[:, N_STATES+1:N_STATES+2])
        b_s_ = torch.FloatTensor(b_memory[:, -N_STATES:])

        q_eval = self.eval_net(b_s).gather(1, b_a)
        q_next = self.target_net(b_s_).detach()
        q_target = b_r + GAMMA * q_next.max(1)[0].view(BATCH_SIZE, 1)
        loss = self.loss_func(q_eval, q_target)
        tempLoss = loss.item()
        runningLoss.append(tempLoss)
        self.optimizer.zero_grad()                                      
        loss.backward()                                                 
        self.optimizer.step()                                           

dqn = DQN()
rospy.init_node('DQN', anonymous=True)
pub = rospy.Publisher('action', Int32, queue_size=10) 

def keyboardCallback(data) :
    global startMark, startLearn
    if data.data == 's':
        startMark = 1
    if data.data == 'w':
        startMark = 0
    if data.data == 'l':
        startLearn = 1

def callback(data) : #receive data from datamerge
    global dqn, pub, startMark, startTime
    maxDistance = 8.0
    s = [data.s.distance, data.s.x, data.s.y, data.s.Position]
    s_ = [data.newS.distance, data.newS.x, data.newS.y, data.newS.Position]
    timeR = min((3000 - (time.time() - startTime)) / 3000, 0)
    print(timeR)
    r = float(data.r) + (maxDistance - data.newS.distance) / maxDistance + timeR
    a = dqn.choose_action(s)     
    rewardMemory.append([s, a, r, s_])                                   
    pub.publish(a)            

if __name__ == '__main__':
    rospy.Subscriber('/dataFrame', dataFrame, callback)
    rospy.Subscriber('/keyboardInput', String, keyboardCallback)
    k = 0
    for i in range(400):                                                   
        print('<<<<<<<<<round: %s' % i)
        startMark = -1
        startLearn = 0
        while(startMark != 1):                                                
            pass
        startTime = time.time()
        ####
        #reward feedback
        while(startLearn == 0) :
            pass
        if rewardMemory != [] :
            s, a, r, s_ = rewardMemory.pop()
            #data = pd.DataFrame(s + [a,r] + s_)
            #print(s + [a,r] + s_)
            #data.to_csv('csv_data.csv', sep=',', encoding='utf-8', header= False, index = False,mode='a') #save data to csv if need but it causes lag
            dqn.store_transition(s, a, r, s_) 
            rInput = r
        while rewardMemory != [] :
            s, a, r, s_ = rewardMemory.pop()
            r = r + rInput
            rInput *= 0.95
            #data = pd.DataFrame(s + [a,r] + s_)
            #print(s + [a,r] + s_)
            #data.to_csv('csv_data.csv', sep=',', encoding='utf-8', header= False, index = False,mode='a')
            dqn.store_transition(s, a, r, s_)      
        ####
        if dqn.memory_counter > MEMORY_CAPACITY:
            dqn.learn()
            k += 1
            output = torch.tensor(runningLoss)
            torch.save(output, model_dir + '/loss/epoch_{}'.format(k))
            print('epoch' + str(k) + 'end')
