import matplotlib.pyplot as plt
import torch
import numpy as np

def plot_loss(n):
    y = []
    model_dir = '/home/jubileus/motor/src/dynamixel_motor/model/withoutPWM/loss'
    #enc = np.load('D:\MobileNet_v1\plan1-AddsingleLayer\loss\epoch_{}.npy'.format(i))
    enc = torch.load(model_dir + '/epoch_{}'.format(n))
    #enc2 = torch.load(model_dir + '/epoch_{}'.format(50))
    #tempy = list(enc2)
    tempy = list(enc)
    #lastx = 3.0
    k = 0
    for x in tempy :
        k += 1
    #    if x >= 5.0 or (k > 40 and x > 3.0):
    #        y.append(lastx)
    #    else :
        y.append(x / 1000) 
    #    lastx = x
    print(y)
    x = range(0,len(y))
    plt.plot(x, y, '.-')
    plt_title = 'BATCH_SIZE = 32; LEARNING_RATE:0.01'
    plt.title(plt_title)
    plt.xlabel('per 10 times')
    plt.ylabel('LOSS')
    plt.savefig(model_dir + '/loss_{}'.format(n))
   # plt.show()

if __name__ == "__main__":
    plot_loss(100)
