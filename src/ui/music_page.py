#!/usr/bin/env python3
"""
音乐页面模块

此模块提供音乐播放功能界面，使用 MPlayer 实现。
"""
import os
import sys
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSlider,
    QListWidget, QListWidgetItem, QHBoxLayout, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

class MusicPage(QWidget):
    """
    音乐页面类
    
    提供音乐播放功能界面。
    """
    
    # 自定义信号
    back_requested = pyqtSignal()
    
    def __init__(self):
        """初始化音乐页面"""
        super().__init__()
        self.music_files = []  # 音乐文件列表
        self.current_music_index = 0  # 当前播放的音乐索引
        self.mplayer_process = None  # MPlayer 进程
        self.is_playing = False  # 播放状态
        self.current_volume = 80  # 当前音量
        self.init_ui()
        self.scan_music()  # 扫描音乐文件
    
    def init_ui(self):
        """初始化UI"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 创建标题标签
        title_label = QLabel("音乐播放")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("WenQuanYi Micro Hei", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #FFD700; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 3px;")
        layout.addWidget(title_label)
        
        # 创建当前播放信息区域
        info_widget = QWidget()
        info_widget.setStyleSheet("background-color: rgba(0,0,0,0.3); border-radius: 3px;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(5, 5, 5, 5)
        
        # 当前播放歌曲名
        self.now_playing_label = QLabel("未在播放")
        self.now_playing_label.setAlignment(Qt.AlignCenter)
        self.now_playing_label.setFont(QFont("WenQuanYi Micro Hei", 12, QFont.Bold))
        self.now_playing_label.setStyleSheet("color: #FFD700;")
        info_layout.addWidget(self.now_playing_label)
        
        # 播放进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555;
                border-radius: 2px;
                background-color: #333;
                color: #FFD700;
                font-size: 9px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 2px;
            }
        """)
        info_layout.addWidget(self.progress_bar)
        
        layout.addWidget(info_widget)
        
        # 创建播放列表
        self.music_list = QListWidget()
        self.music_list.setStyleSheet("""
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
        self.music_list.setFixedHeight(100)
        self.music_list.itemClicked.connect(self.on_music_selected)
        layout.addWidget(self.music_list)
        
        # 创建音量控制
        volume_layout = QHBoxLayout()
        volume_label = QLabel("音量:")
        volume_label.setStyleSheet("color: #FFD700; font-size: 10px;")
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.current_volume)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #555;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #FFD700;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_value_label = QLabel(f"{self.current_volume}%")
        self.volume_value_label.setStyleSheet("color: #FFD700; font-size: 10px;")
        self.volume_value_label.setFixedWidth(30)
        volume_layout.addWidget(self.volume_value_label)
        
        layout.addLayout(volume_layout)
        
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
        stop_btn.clicked.connect(self.stop_music)
        controls_layout.addWidget(stop_btn)
        
        # 上一首按钮
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
        
        # 下一首按钮
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
        
        # 创建定时器更新进度
        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(1000)  # 每秒更新一次
        self.progress_timer.timeout.connect(self.update_progress)
    
    def scan_music(self):
        """扫描音乐文件"""
        # 在ARM设备上扫描音乐目录
        music_dirs = [
            "/qt/project_v1/music",
            "/home/music",
            "/mnt/sdcard/music",
            "/media/music",
            "/mnt/usb/music"
        ]
        
        music_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma']
        
        for music_dir in music_dirs:
            if os.path.exists(music_dir):
                try:
                    for file in os.listdir(music_dir):
                        if any(file.lower().endswith(ext) for ext in music_extensions):
                            full_path = os.path.join(music_dir, file)
                            if os.path.isfile(full_path):
                                self.music_files.append(full_path)
                                # 添加到列表显示
                                item = QListWidgetItem(os.path.basename(file))
                                item.setData(Qt.UserRole, full_path)
                                self.music_list.addItem(item)
                except Exception as e:
                    print(f"扫描目录 {music_dir} 失败: {e}")
        
        if self.music_files:
            self.status_label.setText(f"找到 {len(self.music_files)} 首音乐")
        else:
            self.status_label.setText("未找到音乐文件")
            # 添加示例项
            item = QListWidgetItem("示例音乐 (请添加音乐文件)")
            self.music_list.addItem(item)
    
    def on_music_selected(self, item):
        """音乐被选中"""
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self.play_music(file_path)
    
    def play_music(self, file_path):
        """播放指定音乐"""
        # 先停止当前播放
        self.stop_music()
        
        if not os.path.exists(file_path):
            self.status_label.setText(f"文件不存在: {file_path}")
            return
        
        try:
            # 使用 ffmpeg 解码 + aplay 播放（管道方式）
            # ffmpeg 解码为 wav 格式，通过管道送给 aplay
            cmd = f"ffmpeg -i '{file_path}' -f wav - 2>/dev/null | aplay -D hw:0,0 -"
            
            # 启动播放进程（使用 shell 执行管道命令）
            self.mplayer_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            self.is_playing = True
            self.now_playing_label.setText(os.path.basename(file_path))
            self.status_label.setText(f"正在播放: {os.path.basename(file_path)}")
            self.play_btn.setText("❚❚")
            
            print(f"开始播放音乐: {file_path}")
            
        except Exception as e:
            self.status_label.setText(f"播放失败: {str(e)}")
            print(f"播放音乐失败: {e}")
    
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
        elif self.music_files:
            # 如果没有正在播放，播放第一首音乐
            self.play_music(self.music_files[self.current_music_index])
    
    def stop_music(self):
        """停止播放"""
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
                print(f"停止音乐失败: {e}")
                try:
                    self.mplayer_process.kill()
                    self.mplayer_process.wait()
                except:
                    pass
            
            self.mplayer_process = None
        
        self.is_playing = False
        self.play_btn.setText("▶")
        self.now_playing_label.setText("未在播放")
        self.status_label.setText("已停止")
        self.progress_timer.stop()
        self.progress_bar.setValue(0)
        
        # 强制垃圾回收，释放内存
        import gc
        gc.collect()
    
    def play_previous(self):
        """播放上一首"""
        if self.music_files:
            self.current_music_index = (self.current_music_index - 1) % len(self.music_files)
            self.play_music(self.music_files[self.current_music_index])
            self.music_list.setCurrentRow(self.current_music_index)
    
    def play_next(self):
        """播放下一首"""
        if self.music_files:
            self.current_music_index = (self.current_music_index + 1) % len(self.music_files)
            self.play_music(self.music_files[self.current_music_index])
            self.music_list.setCurrentRow(self.current_music_index)
    
    def set_volume(self, volume):
        """设置音量"""
        self.current_volume = volume
        self.volume_value_label.setText(f"{volume}%")
        
        # 如果正在播放，发送音量命令
        if self.mplayer_process and self.is_playing:
            try:
                self.mplayer_process.stdin.write(f'volume {volume} 1\n'.encode())
                self.mplayer_process.stdin.flush()
            except Exception as e:
                print(f"设置音量失败: {e}")
    
    def update_progress(self):
        """更新播放进度"""
        if self.mplayer_process:
            # 检查进程是否还在运行
            if self.mplayer_process.poll() is not None:
                # 播放结束
                self.is_playing = False
                self.play_btn.setText("▶")
                self.status_label.setText("播放结束")
                self.progress_timer.stop()
                self.progress_bar.setValue(0)
                
                # 自动播放下一首
                if self.music_files:
                    self.play_next()
            else:
                # 模拟进度更新（MPlayer 不直接提供进度信息）
                current_value = self.progress_bar.value()
                if current_value < 100:
                    self.progress_bar.setValue(current_value + 1)
    
    def on_back(self):
        """返回按钮处理"""
        self.stop_music()
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
        elif key_code == 97:  # 按键3 - 上一首
            self.play_previous()
        elif key_code == 96:  # 按键4 - 下一首
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
            # 左键上一首
            self.play_previous()
        elif event.key() == Qt.Key_Right:
            # 右键下一首
            self.play_next()
    
    def closeEvent(self, event):
        """关闭事件"""
        self.stop_music()
        super().closeEvent(event)
