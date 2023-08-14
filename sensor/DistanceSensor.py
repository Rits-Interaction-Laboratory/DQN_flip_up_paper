# coding: UTF-8

# arduinoからシリアル通信受信して温度をモニター

import sys
import os
import serial
# importはカレントディレクトリもまわるので，このスクリプト名をserial.pyにすると動かない！

def main(args):
    # while True:
    if True:
        # timeoutを秒で設定．ボーレートはデフォルトで9600．
        ser = serial.Serial('/dev/ttyACM0', timeout=5.0)

        # 1文字読み込み
        # c = ser.read()
        # 指定文字数読み込み ただしtimeoutが設定されている場合は読み取れた分だけ
        # str = ser.read(10)
        # 行終端'¥n'までリードする
        # line = ser.readline()

        # 最初に届く行は不完全な可能性があるので捨てる．
        line1 = ser.readline()
        line2 = ser.readline()
        ser.close()

		# 改行コードの削除．
        # line2.strip()
        # これだと，LFのみでCRLFは消せない．
        # ArduinoはWindowsから書き込みしているのでCRLF．
        line2 = line2.replace('\n','')
        line2 = line2.replace('\r','')
        ps(line2)

def ps(output):
    sys.stdout.write(str(output))
    sys.stdout.flush()

if __name__ == '__main__':
    main(sys.argv)
