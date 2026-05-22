import serial
import time

# 确保端口号和波特率对得上
ser = serial.Serial('/dev/ttyACM0', 115200) 
time.sleep(2) # 等待单片机重启完成

print("发送 w 指令...")
ser.write(b'w\n') # 注意这里的 \n 极其重要！

# 停顿 2 秒，给单片机一点执行的时间，严禁死循环疯狂轰炸
time.sleep(2)