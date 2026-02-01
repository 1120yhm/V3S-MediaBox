#!/usr/bin/env python3
"""
ARM设备按键映射模块

此模块提供ARM开发板物理按键到Qt按键码的映射功能。
"""

import os
import sys
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QKeyEvent

class ARMKeyMapper(QObject):
    """
    ARM设备按键映射器
    
    将ARM开发板的物理按键映射到Qt按键码。
    """
    
    # 自定义信号，用于发送按键事件
    key_pressed = pyqtSignal(QKeyEvent)
    
    def __init__(self, parent=None):
        """
        初始化按键映射器
        
        Args:
            parent (QObject, optional): 父对象. Defaults to None.
        """
        super().__init__(parent)
        # 按键映射字典，根据实际硬件按键码调整
        # 根据hexdump输出解析的按键码
        self.key_map = {
            # 从hexdump解析的按键码
            115: Qt.Key_Up,      # 按键1 (0x73) - 上键
            114: Qt.Key_Down,    # 按键2 (0x72) - 下键
            97: Qt.Key_Left,     # 按键3 (0x61) - 左键
            96: Qt.Key_Right,    # 按键4 (0x60) - 右键
            
            # 如果需要确认键，可以添加第五个按键
            # 28: Qt.Key_Return,   # 确认键/回车键
            
            # 备用映射方案（使用长按或组合键）
            # 如果长按按键1可以当作确认键
            # 115: Qt.Key_Return,  # 长按按键1作为确认键
        }
    
    def map_key(self, hw_key_code):
        """
        将硬件按键码映射到Qt按键码
        
        Args:
            hw_key_code (int): 硬件按键码
            
        Returns:
            int: Qt按键码，如果未找到映射则返回0
        """
        return self.key_map.get(hw_key_code, 0)
    
    def create_key_event(self, hw_key_code, pressed=True):
        """
        创建按键事件
        
        Args:
            hw_key_code (int): 硬件按键码
            pressed (bool, optional): 是否按下. Defaults to True.
            
        Returns:
            QKeyEvent: 按键事件对象
        """
        qt_key_code = self.map_key(hw_key_code)
        if qt_key_code:
            if pressed:
                return QKeyEvent(QKeyEvent.KeyPress, qt_key_code, Qt.NoModifier)
            else:
                return QKeyEvent(QKeyEvent.KeyRelease, qt_key_code, Qt.NoModifier)
        return None