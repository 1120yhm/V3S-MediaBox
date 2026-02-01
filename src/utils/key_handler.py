#!/usr/bin/env python3
"""
按键处理模块

此模块提供ARM开发板物理按键的处理功能。
"""
import os
import sys
import threading
import struct
from PyQt5.QtCore import QObject, pyqtSignal

class KeyHandler(QObject):
    """
    按键处理器
    
    处理ARM开发板物理按键事件。
    """
    
    # 自定义信号，用于发送按键码
    key_pressed = pyqtSignal(int)
    key_released = pyqtSignal(int)
    
    def __init__(self, device_path='/dev/input/event0'):
        """
        初始化按键处理器
        
        Args:
            device_path (str): 输入设备路径，默认为'/dev/input/event0'
        """
        super().__init__()
        self.device_path = device_path
        self.running = False
        
        # 按键映射字典，根据实际硬件按键码调整
        self.key_map = {
            # 根据hexdump输出得到的按键码
            115: "key1",  # 按键1 (0x73)
            114: "key2",  # 按键2 (0x72)
            97: "key3",   # 按键3 (0x61)
            96: "key4",    # 按键4 (0x60)
        }
    
    def start_reading(self):
        """开始读取输入设备"""
        self.running = True
        # 在单独的线程中读取输入设备
        self.thread = threading.Thread(target=self._read_device)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_reading(self):
        """停止读取输入设备"""
        self.running = False
    
    def _read_device(self):
        """读取输入设备的线程函数"""
        try:
            with open(self.device_path, 'rb') as device:
                while self.running:
                    # 读取事件
                    data = device.read(16)
                    if len(data) == 16:
                        # 解析事件 - 使用16字节结构
                        # 根据hexdump输出分析：
                        # b0 1a 00 00 11 f6 06 00 01 00 73 00 01 00 00 00
                        # 0-7: 时间戳 (8字节)
                        # 8: 类型 (1字节)
                        # 9: 保留 (1字节)
                        # 10-11: 代码 (2字节)
                        # 12: 值 (1字节)
                        # 13-15: 保留 (3字节)
                        
                        # 使用更简单的方式解析
                        type = data[8]
                        code = data[10]
                        value = data[12]
                        
                        # 处理按键事件
                        if type == 1:
                            if value == 1:
                                print(f"检测到按键按下: code={code}, name={self.key_map.get(code, 'unknown')}")
                                # 发送按键按下信号
                                self.key_pressed.emit(code)
                            elif value == 0:
                                print(f"检测到按键释放: code={code}, name={self.key_map.get(code, 'unknown')}")
                                # 发送按键释放信号
                                self.key_released.emit(code)
        except Exception as e:
            print(f"读取输入设备失败: {e}")
    
    def get_key_name(self, key_code):
        """
        获取按键名称
        
        Args:
            key_code (int): 按键码
            
        Returns:
            str: 按键名称
        """
        return self.key_map.get(key_code, "unknown")