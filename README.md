# DQN_flip_up_paper

Python 3.8
ROS melodic
Ubuntu 18.04
robot hand setup : <p>https://kb.seedrobotics.com/doku.php?id=start</p>

## 起動順番：
### dynamixel　サーバー起動
<code>
  sudo chmod 777 /dev/ttyUSB0
  roslaunch work controller_manager.launch 
  roslaunch work start.launch
</code>
All IO API are defined in DQN_flip_up_paper/dynamixel_driver/src/dynamixel_io.py
And parameter address are defined in DQN_flip_up_paper/dynamixel_driver/src/dynamixel_const.py

### センサーのポート起動
<code>
  python sensor.py
</code>

If raise errors of data size just rerun this file

### キーボード入力
<code>
  python teleop.py
</code>

no feedback

### ロボットハンド制御システム
<code>
  python mainCtrl.py
</code>
main control method is defined here
the distance gap is calculated in main function
Action is received in ROS feedback
send hand motor information to datamerge 

### data merge
<code>
  python DataMerge.py
</code>
merge the sensor data and motor data
Input reward here each epoch

### DQN training(When training)
<code>
  python DQNTrain.py
</code>
DQN is defined here and calculate the InputReward here

### DQN testing(When testing)
<code>
  python DQNTest.py
</code>
need to input the trained model

# When training
1.execute the above files
2.input 'w' in teleop(after DQN shows ">>>epoch XX")
3.input 's' in teleop when finish
4.input reward in datamerge
5.loop 1-4 until tarining process end
