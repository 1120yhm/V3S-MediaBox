#!/usr/bin/env python3
"""
视频页面模块

此模块提供视频播放功能界面，使用 MPlayer 实现。
"""
import os
import sys
import subprocess
import signal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSlider,
    QListWidget, QListWidgetItem, QHBoxLayout, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QProcess
from PyQt5.QtGui import QFont, QWindow

class VideoPage(QWidget):
    """
    视频页面类
    
    提供视频播放功能界面。
    """
    
    # 自定义信号
    back_requested = pyqtSignal()
    
    def __init__(self):
        """初始化视频页面"""
        super().__init__()
        self.video_files = []  # 视频文件列表
        self.current_video_index = 0  # 当前播放的视频索引
        self.mplayer_process = None  # MPlayer 进程
        self.is_playing = False  # 播放状态
        self.init_ui()
        self.scan_videos()  # 扫描视频文件
    
    def init_ui(self):
        """初始化UI"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 创建标题标签
        title_label = QLabel("视频播放")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("WenQuanYi Micro Hei", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #FFD700; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 3px;")
        layout.addWidget(title_label)
        
        # 创建视频播放区域（使用 QFrame 作为容器）
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setFixedSize(230, 150)
        layout.addWidget(self.video_frame)
        
        # 创建视频列表
        self.video_list = QListWidget()
        self.video_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(0, 0, 0, 0.7);
                color: #FFD700;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 3px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        self.video_list.setFixedHeight(60)
        self.video_list.itemClicked.connect(self.on_video_selected)
        layout.addWidget(self.video_list)
        
        # 创建控制按钮区域
        controls_layout = QHBoxLayout()
        
        # 播放/暂停按钮
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 30)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        self.play_btn.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_btn)
        
        # 停止按钮
        stop_btn = QPushButton("■")
        stop_btn.setFixedSize(40, 30)
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
            }
        """)
        stop_btn.clicked.connect(self.stop_video)
        controls_layout.addWidget(stop_btn)
        
        # 上一个按钮
        prev_btn = QPushButton("◀")
        prev_btn.setFixedSize(40, 30)
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)
        prev_btn.clicked.connect(self.play_previous)
        controls_layout.addWidget(prev_btn)
        
        # 下一个按钮
        next_btn = QPushButton("▶")
        next_btn.setFixedSize(40, 30)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)
        next_btn.clicked.connect(self.play_next)
        controls_layout.addWidget(next_btn)
        
        # 返回按钮
        back_btn = QPushButton("返回")
        back_btn.setFixedSize(50, 30)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                font-size: 12px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:pressed {
                background-color: #F57C00;
            }
        """)
        back_btn.clicked.connect(self.on_back)
        controls_layout.addWidget(back_btn)
        
        layout.addLayout(controls_layout)
        
        # 创建状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #FFD700; font-size: 10px;")
        layout.addWidget(self.status_label)
        
        # 设置布局
        self.setLayout(layout)
        
        # 创建定时器更新状态
        self.status_timer = QTimer(self)
        self.status_timer.setInterval(1000)
        self.status_timer.timeout.connect(self.update_status)
    
    def scan_videos(self):
        """扫描视频文件 - 只扫描低分辨率版本"""
        # 在ARM设备上扫描视频目录
        video_dirs = [
            "/qt/project_v1/videos",
            "/home/videos",
            "/mnt/sdcard/videos",
            "/media/videos",
            "/mnt/usb/videos"
        ]
        
        # 只扫描低分辨率版本（_180p, _240p, _360p）
        lowres_suffixes = ['_180p.mp4', '_240p.mp4', '_360p.mp4', '_180p.avi', '_240p.avi', '_360p.avi']
        
        for video_dir in video_dirs:
            if os.path.exists(video_dir):
                try:
                    for file in os.listdir(video_dir):
                        # 只添加低分辨率版本
                        if any(file.lower().endswith(suffix) for suffix in lowres_suffixes):
                            full_path = os.path.join(video_dir, file)
                            if os.path.isfile(full_path):
                                self.video_files.append(full_path)
                                # 添加到列表显示
                                item = QListWidgetItem(file)
                                item.setData(Qt.UserRole, full_path)
                                self.video_list.addItem(item)
                except Exception as e:
                    print(f"扫描目录 {video_dir} 失败: {e}")
        
        if self.video_files:
            self.status_label.setText(f"找到 {len(self.video_files)} 个视频文件")
        else:
            self.status_label.setText("未找到视频文件")
            # 添加示例项
            item = QListWidgetItem("示例视频 (请添加视频文件)")
            self.video_list.addItem(item)
    
    def on_video_selected(self, item):
        """视频被选中"""
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self.play_video(file_path)
    
    def play_video(self, file_path):
        """播放指定视频"""
        # 先停止当前播放
        self.stop_video()
        
        if not os.path.exists(file_path):
            self.status_label.setText(f"文件不存在: {file_path}")
            return
        
        try:
            # 使用固定的屏幕位置（根据实际屏幕调整）
            # 获取视频显示框在屏幕上的绝对位置
            video_frame_pos = self.video_frame.mapToGlobal(self.video_frame.rect().topLeft())
            video_x = video_frame_pos.x()
            video_y = video_frame_pos.y()
            video_width = self.video_frame.width()
            video_height = self.video_frame.height()
            
            print(f"视频窗口位置: ({video_x}, {video_y}), 大小: {video_width}x{video_height}")
            
            # 构建 MPlayer 命令 - 直接使用系统 MPlayer
            # 确保能找到 ALSA 库
            cmd = [
                '/usr/bin/mplayer',
                '-vo', 'fbdev2',              # 使用帧缓冲输出
                '-ao', 'alsa',                # 使用 ALSA 音频输出
                '-vf', f'scale={video_width}:{video_height}',  # 视频缩放
                '-geometry', f'{video_x}:{video_y}',  # 精确位置
                '-noborder',                  # 无边框
                '-quiet',                     # 安静模式
                '-really-quiet',              # 更安静
                '-framedrop',                 # 丢弃帧以保持同步
                '-hardframedrop',             # 更激进的帧丢弃
                '-lavdopts', 'lowres=1:fast:skiploopfilter=all',  # 低分辨率、快速解码、跳过环路滤波
                '-cache', '2048',             # 减少缓存到 2MB
                '-cache-min', '10',           # 最小缓存 10%
                '-nomouseinput',              # 禁用鼠标输入，减少内存
                '-noconsolecontrols',         # 禁用控制台控制
                file_path
            ]
            
            # 启动 MPlayer
            self.mplayer_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.PIPE
            )
            
            self.is_playing = True
            self.status_label.setText(f"正在播放: {os.path.basename(file_path)}")
            self.play_btn.setText("❚❚")
            self.status_timer.start()
            
            print(f"开始播放视频: {file_path} 在位置 ({video_x}, {video_y})")
            
        except Exception as e:
            self.status_label.setText(f"播放失败: {str(e)}")
            print(f"播放视频失败: {e}")
    
    def toggle_play(self):
        """切换播放/暂停"""
        if self.mplayer_process and self.is_playing:
            try:
                # 发送暂停命令
                self.mplayer_process.stdin.write(b'pause\n')
                self.mplayer_process.stdin.flush()
                
                # 切换状态
                if self.play_btn.text() == "▶":
                    self.play_btn.setText("❚❚")
                    self.status_label.setText("继续播放")
                else:
                    self.play_btn.setText("▶")
                    self.status_label.setText("已暂停")
            except Exception as e:
                print(f"暂停失败: {e}")
        elif self.video_files:
            # 如果没有正在播放，播放第一个视频
            self.play_video(self.video_files[self.current_video_index])
    
    def stop_video(self):
        """停止播放"""
        # 停止音频进程
        if hasattr(self, 'audio_process') and self.audio_process:
            try:
                self.audio_process.kill()
                self.audio_process.wait(timeout=1)
            except:
                pass
            self.audio_process = None
        
        if self.mplayer_process:
            try:
                # 发送退出命令
                self.mplayer_process.stdin.write(b'quit\n')
                self.mplayer_process.stdin.flush()
                
                # 等待进程结束
                try:
                    self.mplayer_process.wait(timeout=1)
                except:
                    # 超时后强制终止
                    self.mplayer_process.terminate()
                    try:
                        self.mplayer_process.wait(timeout=1)
                    except:
                        self.mplayer_process.kill()
                        self.mplayer_process.wait()
            except Exception as e:
                print(f"停止视频失败: {e}")
                try:
                    self.mplayer_process.kill()
                    self.mplayer_process.wait()
                except:
                    pass
            self.mplayer_process = None
        
        self.is_playing = False
        self.play_btn.setText("▶")
        self.status_label.setText("已停止")
        self.status_timer.stop()
        
        # 强制垃圾回收，释放内存
        import gc
        gc.collect()
    
    def play_previous(self):
        """播放上一个视频"""
        if self.video_files:
            self.current_video_index = (self.current_video_index - 1) % len(self.video_files)
            self.play_video(self.video_files[self.current_video_index])
            self.video_list.setCurrentRow(self.current_video_index)
    
    def play_next(self):
        """播放下一个视频"""
        if self.video_files:
            self.current_video_index = (self.current_video_index + 1) % len(self.video_files)
            self.play_video(self.video_files[self.current_video_index])
            self.video_list.setCurrentRow(self.current_video_index)
    
    def update_status(self):
        """更新播放状态"""
        if self.mplayer_process:
            # 检查进程是否还在运行
            if self.mplayer_process.poll() is not None:
                # 播放结束
                self.is_playing = False
                self.play_btn.setText("▶")
                self.status_label.setText("播放结束")
                self.status_timer.stop()
                
                # 自动播放下一个
                if self.video_files:
                    self.play_next()
    
    def on_back(self):
        """返回按钮处理"""
        self.stop_video()
        self.back_requested.emit()
    
    def handle_key(self, key_code):
        """
        处理按键事件
        
        Args:
            key_code (int): 按键码
        """
        if key_code == 115:  # 按键1 - 播放/暂停
            self.toggle_play()
        elif key_code == 114:  # 按键2 - 返回/停止
            self.on_back()
        elif key_code == 97:  # 按键3 - 上一个
            self.play_previous()
        elif key_code == 96:  # 按键4 - 下一个
            self.play_next()
    
    def keyPressEvent(self, event):
        """
        按键事件处理
        
        Args:
            event: 按键事件
        """
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 返回键触发返回信号
            self.on_back()
        elif event.key() == Qt.Key_Space:
            # 空格键播放/暂停
            self.toggle_play()
        elif event.key() == Qt.Key_Left:
            # 左键上一个
            self.play_previous()
        elif event.key() == Qt.Key_Right:
            # 右键下一个
            self.play_next()
    
    def closeEvent(self, event):
        """关闭事件"""
        self.stop_video()
        super().closeEvent(event)
