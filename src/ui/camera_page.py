#!/usr/bin/env python3
"""
相机页面模块

使用 fswebcam 实现拍照功能（无实时预览）
"""
import os
import sys
import time
import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

class CameraPage(QWidget):
    """
    相机页面类
    
    提供相机功能界面，使用 fswebcam 实现拍照。
    """
    
    # 自定义信号
    back_requested = pyqtSignal()
    
    def __init__(self):
        """初始化相机页面"""
        super().__init__()
        self.camera_device = "/dev/video0"  # 摄像头设备
        self.photo_dir = "/qt/project_v1/photos"  # 照片保存目录
        self.last_photo = None  # 最后拍摄的照片路径
        # 设置固定大小，修复界面偏移
        self.setFixedSize(240, 320)
        self.init_ui()
        self.init_camera()
    
    def init_ui(self):
        """初始化UI"""
        print("开始初始化相机页面UI")
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建标题标签
        title_label = QLabel("相机")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("WenQuanYi Micro Hei", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #FFD700; background-color: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px;")
        layout.addWidget(title_label)
        
        # 创建照片显示区域 - 使用QWidget避免遮挡
        from PyQt5.QtWidgets import QFrame
        self.photo_frame = QFrame()
        self.photo_frame.setFixedSize(220, 140)
        self.photo_frame.setStyleSheet("background-color: #000000; border: 2px solid #555555;")
        self.photo_frame.setFrameShape(QFrame.StyledPanel)
        
        # 照片标签放在frame内
        self.photo_label = QLabel("准备拍照", self.photo_frame)
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setStyleSheet("background-color: transparent; color: white; border: none;")
        self.photo_label.setGeometry(0, 0, 220, 140)
        
        layout.addWidget(self.photo_frame, alignment=Qt.AlignCenter)
        
        # 创建状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # 创建按钮容器
        from PyQt5.QtWidgets import QHBoxLayout, QWidget
        button_container = QWidget()
        button_container.setFixedHeight(50)  # 固定高度
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建确定按钮（缩小）
        self.confirm_button = QPushButton("✓")
        self.confirm_button.setFixedSize(40, 40)
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #388E3C;
            }
        """)
        self.confirm_button.clicked.connect(self.on_back)
        button_layout.addWidget(self.confirm_button)
        
        # 创建拍照按钮
        self.capture_button = QPushButton("📷")
        self.capture_button.setFixedSize(50, 40)
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)
        self.capture_button.clicked.connect(self.take_photo)
        button_layout.addWidget(self.capture_button)
        
        # 创建录像按钮
        self.record_button = QPushButton("⏺")
        self.record_button.setFixedSize(40, 40)
        self.record_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #E64A19;
            }
        """)
        self.record_button.clicked.connect(self.toggle_record)
        button_layout.addWidget(self.record_button)
        
        # 创建播放按钮
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(40, 40)
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #7B1FA2;
            }
        """)
        self.play_button.clicked.connect(self.play_last_video)
        button_layout.addWidget(self.play_button)
        
        layout.addWidget(button_container)
        
        # 设置布局
        self.setLayout(layout)
    
    def init_camera(self):
        """初始化相机"""
        # 创建照片保存目录
        os.makedirs(self.photo_dir, exist_ok=True)
        
        # 检查摄像头设备
        if os.path.exists(self.camera_device):
            self.status_label.setText("摄像头已连接，准备拍照")
            self.photo_label.setText("按拍照按钮开始拍照")
        else:
            self.status_label.setText("未检测到摄像头")
            self.photo_label.setText("未检测到摄像头")
    
    def take_photo(self):
        """拍照"""
        try:
            # 生成照片文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            photo_file = os.path.join(self.photo_dir, f"photo_{timestamp}.jpg")
            
            print(f"使用 fswebcam 拍照: {self.camera_device}")
            
            # 使用测试成功的 fswebcam 命令
            cmd = [
                "fswebcam",
                "-S", "20",                    # 跳过20帧，让摄像头稳定
                "-d", self.camera_device,      # 设备
                "-p", "UYVY",                  # 像素格式
                "-r", "800x600",               # 分辨率
                "--no-banner",                 # 无横幅
                photo_file                     # 输出文件
            ]
            
            self.status_label.setText("正在拍照...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            print(f"fswebcam 输出: {result.stdout}")
            print(f"fswebcam 错误: {result.stderr}")
            
            if os.path.exists(photo_file) and os.path.getsize(photo_file) > 0:
                size = os.path.getsize(photo_file) / 1024
                self.status_label.setText(f"拍照成功: {os.path.basename(photo_file)} ({size:.1f}KB)")
                print(f"拍照保存到: {photo_file}")
                
                # 保存最后拍摄的照片路径
                self.last_photo = photo_file
                
                # 自动显示照片
                self.display_photo(photo_file)
                
                # 拍照成功，不需要启用查看按钮（已删除）
                pass
            else:
                self.status_label.setText("拍照失败")
                print("拍照失败")
                    
        except Exception as e:
            error_msg = str(e)
            self.status_label.setText(f"拍照失败: {error_msg}")
            print(f"拍照失败: {e}")
    
    def display_photo(self, photo_path):
        """显示照片"""
        try:
            from PyQt5.QtGui import QTransform
            
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                # 垂直翻转（修复上下颠倒）
                transform = QTransform()
                transform.scale(1, -1)
                flipped_pixmap = pixmap.transformed(transform)
                
                # 获取 photo_label 的尺寸进行缩放（减去边框）
                label_width = self.photo_frame.width() - 4  # 减去左右边框 2+2
                label_height = self.photo_frame.height() - 4  # 减去上下边框 2+2
                scaled_pixmap = flipped_pixmap.scaled(
                    label_width,
                    label_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.photo_label.setPixmap(scaled_pixmap)
                self.photo_label.setAlignment(Qt.AlignCenter)
                self.photo_label.setText("")
            else:
                self.photo_label.setText("无法加载照片")
        except Exception as e:
            print(f"显示照片失败: {e}")
            self.photo_label.setText("显示照片失败")
    
    def view_photo(self):
        """查看最后拍摄的照片"""
        if self.last_photo and os.path.exists(self.last_photo):
            self.display_photo(self.last_photo)
            self.status_label.setText(f"查看照片: {os.path.basename(self.last_photo)}")
        else:
            QMessageBox.information(self, "提示", "没有可查看的照片")
    
    def on_back(self):
        """返回按钮处理"""
        # 如果正在录像，先停止
        if hasattr(self, 'is_recording') and self.is_recording:
            self.stop_record()
        self.back_requested.emit()

    def toggle_record(self):
        """切换录像状态"""
        print("录像按钮被点击")
        try:
            if hasattr(self, 'is_recording') and self.is_recording:
                print("停止录像")
                self.stop_record()
            else:
                print("开始录像")
                self.start_record()
        except Exception as e:
            self.status_label.setText(f"录像失败: {str(e)}")
            print(f"录像失败: {e}")

    def start_record(self):
        """开始录像"""
        try:
            # 生成视频文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            video_file = os.path.join(self.photo_dir, f"video_{timestamp}.avi")
            self.current_video = video_file
            
            print(f"开始录像: {video_file}")
            
            # 使用降低分辨率的 ffmpeg 命令，减少内存使用
            # 摄像头只支持 800x600，使用更低的帧率和编码器选项
            cmd = [
                "ffmpeg",
                "-f", "video4linux2",
                "-s", "800x600",
                "-r", "5",
                "-i", self.camera_device,
                "-vf", "vflip,scale=320:240",
                "-c:v", "mpeg4",
                "-q:v", "5",
                "-y",
                video_file
            ]
            
            print(f"执行命令: {' '.join(cmd)}")
            
            self.status_label.setText("正在录像...")
            self.record_button.setText("⏹")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:pressed {
                    background-color: #D32F2F;
                }
            """)
            
            # 启动录像进程，启用 stdin 以便发送停止信号
            self.record_process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.is_recording = True
            
        except Exception as e:
            self.status_label.setText(f"开始录像失败: {str(e)}")
            print(f"开始录像失败: {e}")

    def stop_record(self):
        """停止录像"""
        try:
            if hasattr(self, 'record_process') and self.record_process:
                # 发送 'q' 键给 ffmpeg，让它优雅地停止并写入文件尾
                try:
                    self.record_process.stdin.write(b'q')
                    self.record_process.stdin.flush()
                except:
                    pass
                
                # 等待 ffmpeg 正常退出（最多等待 3 秒）
                try:
                    self.record_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # 如果 3 秒后还没退出，强制终止
                    self.record_process.terminate()
                    self.record_process.wait()
                
                self.record_process = None
            
            self.is_recording = False
            self.record_button.setText("⏺")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF5722;
                    color: white;
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:pressed {
                    background-color: #E64A19;
                }
            """)
            
            self.status_label.setText("录像完成")
            print("录像完成")
            
        except Exception as e:
            self.status_label.setText(f"停止录像失败: {str(e)}")
            print(f"停止录像失败: {e}")

    def handle_key(self, key_code):
        """
        处理按键事件
        
        Args:
            key_code (int): 按键码
        """
        print(f"相机页面按键按下: {key_code}")
        if key_code == 115:  # 按键1 - 拍照/重新拍照
            print("按键1: 拍照/重新拍照")
            # 如果当前正在显示照片，则重新拍照；否则直接拍照
            self.take_photo()
        elif key_code == 114:  # 按键2 - 返回
            print("按键2: 返回")
            self.on_back()
        elif key_code == 97:  # 按键3 - 录像/停止录像
            print("按键3: 录像/停止录像")
            self.toggle_record()
        elif key_code == 96:  # 按键4 - 播放当前录制的视频
            print("按键4: 播放当前录制的视频")
            self.play_last_video()
    
    def play_last_video(self):
        """播放最后录制的视频"""
        try:
            # 查找最新的视频文件
            video_files = [f for f in os.listdir(self.photo_dir) if f.startswith("video_") and f.endswith(".avi")]
            if video_files:
                # 按时间排序，获取最新的视频
                video_files.sort(reverse=True)
                latest_video = os.path.join(self.photo_dir, video_files[0])
                
                print(f"播放视频: {latest_video}")
                self.status_label.setText(f"正在播放: {video_files[0]}")
                
                # 使用 mplayer 播放视频
                cmd = ["mplayer", "-vo", "fbdev2", "-fs", "-zoom", "-x", "240", "-y", "180", latest_video]
                subprocess.run(cmd, timeout=60)
                
                self.status_label.setText("播放完成")
                print("播放完成")
            else:
                self.status_label.setText("没有可播放的视频")
                print("没有可播放的视频")
        except Exception as e:
            self.status_label.setText(f"播放失败: {str(e)}")
            print(f"播放失败: {e}")
    
    def keyPressEvent(self, event):
        """
        按键事件处理
        
        Args:
            event: 按键事件
        """
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 返回键触发返回信号
            self.on_back()
