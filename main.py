#!/usr/bin/env python3
"""
程序入口文件

此文件是应用程序的主入口，负责初始化PyQt5应用程序并启动主界面。

依赖库：
- os：提供操作系统相关功能
- sys：提供系统相关功能
- PyQt5.QtWidgets：提供GUI组件
- PyQt5.QtCore：提供核心功能
- src.ui.main_ui.WeatherMediaUI：主界面类
- src.utils.key_handler.KeyHandler：按键处理类
"""
import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from src.ui.main_ui import WeatherMediaUI
from src.ui.camera_page import CameraPage
from src.ui.video_page import VideoPage
from src.ui.music_page import MusicPage
from src.ui.photo_page import PhotoPage
from src.utils.key_handler import KeyHandler

# ARM环境配置
# 设置Qt平台插件为LinuxFB，解决EGL相关问题
os.environ['QT_QPA_PLATFORM'] = 'linuxfb'
# 指定帧缓冲设备
os.environ['QT_QPA_LINUXFB_FB'] = '/dev/fb0'
# 禁用鼠标光标（对于触摸屏设备）
os.environ['QT_QPA_EGLFS_HIDECURSOR'] = '1'

# 如果LinuxFB不工作，可以尝试以下其他选项（取消注释相应行）：
# os.environ['QT_QPA_PLATFORM'] = 'eglfs'  # 默认选项（当前失败的）
# os.environ['QT_QPA_PLATFORM'] = 'minimal'  # 最小平台
# os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # 离屏渲染（无显示）
# os.environ['QT_QPA_PLATFORM'] = 'xcb'  # 如果有X服务器

class MediaApp(QMainWindow):
    """
    多媒体应用程序类
    
    管理主界面和各个功能页面。
    """
    
    def __init__(self):
        """初始化应用程序"""
        super().__init__()
        
        # 创建应用程序实例
        self.app = QApplication(sys.argv)
        
        # 创建主界面
        self.main_ui = WeatherMediaUI()
        
        # 创建功能页面
        self.camera_page = CameraPage()
        self.video_page = VideoPage()
        self.music_page = MusicPage()
        self.photo_page = PhotoPage()
        
        # 创建页面堆栈
        self.stack = QStackedWidget()
        self.stack.addWidget(self.main_ui)
        self.stack.addWidget(self.camera_page)
        self.stack.addWidget(self.video_page)
        self.stack.addWidget(self.music_page)
        self.stack.addWidget(self.photo_page)
        
        # 连接信号
        self.connect_signals()
        
        # 设置主窗口
        self.setCentralWidget(self.stack)
        self.show()
    
    def exec_(self):
        """运行应用程序事件循环"""
        return self.app.exec_()
    
    def connect_signals(self):
        """连接信号和槽"""
        # 连接主界面的功能选择信号
        self.main_ui.camera_selected.connect(self.show_camera_page)
        self.main_ui.video_selected.connect(self.show_video_page)
        self.main_ui.music_selected.connect(self.show_music_page)
        self.main_ui.photo_selected.connect(self.show_photo_page)
        
        # 连接各页面的返回信号
        self.camera_page.back_requested.connect(self.show_main_page)
        self.video_page.back_requested.connect(self.show_main_page)
        self.music_page.back_requested.connect(self.show_main_page)
        self.photo_page.back_requested.connect(self.show_main_page)
    
    def show_main_page(self):
        """显示主页面"""
        self.stack.setCurrentWidget(self.main_ui)
    
    def show_camera_page(self):
        """显示相机页面"""
        self.stack.setCurrentWidget(self.camera_page)
    
    def show_video_page(self):
        """显示视频页面"""
        self.stack.setCurrentWidget(self.video_page)
    
    def show_music_page(self):
        """显示音乐页面"""
        self.stack.setCurrentWidget(self.music_page)
    
    def show_photo_page(self):
        """显示相册页面"""
        self.stack.setCurrentWidget(self.photo_page)

if __name__ == '__main__':
    """主函数
    
    初始化应用程序，创建主窗口并显示。
    """
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MediaApp()
    
    # 创建按键处理器
    key_handler = KeyHandler('/dev/input/event0')
    
    # 定义按键分发函数
    def dispatch_key_press(key_code):
        """根据当前页面分发按键事件"""
        current_widget = window.stack.currentWidget()
        if current_widget == window.main_ui:
            window.main_ui.handle_raw_key_code(key_code)
        elif current_widget == window.video_page:
            window.video_page.handle_key(key_code)
        elif current_widget == window.camera_page:
            # 相机页面按键处理
            window.camera_page.handle_key(key_code)
        elif current_widget == window.music_page:
            window.music_page.handle_key(key_code)
        elif current_widget == window.photo_page:
            # 相册页面按键处理
            window.photo_page.handle_key(key_code)
    
    # 连接按键信号
    key_handler.key_pressed.connect(dispatch_key_press)
    key_handler.key_released.connect(window.main_ui.handle_key_release)
    
    # 开始读取输入设备
    key_handler.start_reading()
    
    # 运行应用程序事件循环
    exit_code = window.exec_()
    
    # 停止读取输入设备
    key_handler.stop_reading()
    sys.exit(exit_code)