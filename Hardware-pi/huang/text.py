import serial
import struct
import time

# === 配置区域 ===
# 请根据你的实际连接方式修改串口号
# 树莓派自带串口通常为 '/dev/serial0'，USB转TTL通常为 '/dev/ttyUSB0'
SERIAL_PORT = '/dev/ttyAMA3' 
BAUDRATE = 115200

# === 数据包格式定义 ===
# C 结构体使用了 #pragma pack(1)，因此没有内存对齐填充
# <  : Little-endian (ARM 架构默认小端模式)
# B  : uint8_t (head)      -> 1 byte
# h  : int16_t (ax)        -> 2 bytes
# h  : int16_t (ay)        -> 2 bytes
# h  : int16_t (az)        -> 2 bytes
# H  : uint16_t (svm_val)  -> 2 bytes
# B  : uint8_t (is_fall)   -> 1 byte
# i  : int (heart_rate)    -> 4 bytes (32位系统下通常为4字节)
# i  : int (breath_rate)   -> 4 bytes
# B  : uint8_t (has_human) -> 1 byte
# B  : uint8_t (tail)      -> 1 byte
PACKET_FORMAT = '<BhhhHBiiBB'
PACKET_SIZE = struct.calcsize(PACKET_FORMAT) # 计算结果应为 20 字节

def main():
    print(f"预期数据包大小: {PACKET_SIZE} 字节")
    
    try:
        # 初始化串口
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
        print(f"正在监听 {SERIAL_PORT} (波特率: {BAUDRATE})...")
        print("-" * 50)
        
        while True:
            # 等待串口有数据
            if ser.in_waiting > 0:
                # 逐个字节读取，寻找包头 0xAA
                byte = ser.read(1)
                if byte == b'\xAA':
                    # 找到包头，读取剩余的 19 个字节
                    rest_of_packet = ser.read(PACKET_SIZE - 1)
                    
                    if len(rest_of_packet) == PACKET_SIZE - 1:
                        # 拼凑完整的数据包
                        full_packet = byte + rest_of_packet
                        
                        # 检查包尾 0x55 (十进制的85)
                        if full_packet[-1] == 0x55:
                            # 按照指定的格式解包
                            unpacked_data = struct.unpack(PACKET_FORMAT, full_packet)
                            
                            # 提取对应字段
                            head = unpacked_data[0]
                            ax, ay, az = unpacked_data[1], unpacked_data[2], unpacked_data[3]
                            svm = unpacked_data[4]
                            is_fall = unpacked_data[5]
                            hr = unpacked_data[6]
                            br = unpacked_data[7]
                            human = unpacked_data[8]
                            tail = unpacked_data[9]
                            
                            # 格式化打印结果，与 C 端 safe_print 保持类似风格
                            print(f"[DATA] Fall:{is_fall} (SVM:{svm}) | Human:{human} | HR:{hr} | BR:{br} | ACC:({ax},{ay},{az})")
                        else:
                            # 包尾不对，说明数据可能错位了，丢弃该包
                            print(f"[WARNING] 发现错误包尾: {hex(full_packet[-1])}，已丢弃")
                    else:
                        print("[WARNING] 数据包长度不足，等待下一帧...")
                        
    except serial.SerialException as e:
        print(f"\n[ERROR] 串口错误: {e}")
        print("请检查连线，或者确认是否有权限访问该串口 (sudo usermod -aG dialout $USER)")
    except KeyboardInterrupt:
        print("\n[INFO] 用户终止程序")
    finally:
        # 安全关闭串口
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("[INFO] 串口已关闭")

if __name__ == '__main__':
    main()
