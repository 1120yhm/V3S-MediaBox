#!/usr/bin/env python3
"""
相册页面模块

此模块提供图片浏览功能界面，显示拍照和录像的缩略图。
"""
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QGridLayout, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

class PhotoPage(QWidget):
    """
    相册页面类
    
    提供图片浏览功能界面。
    """
    
    # 自定义信号
    back_requested = pyqtSignal()
    
    def __init__(self):
        """初始化相册页面"""
        super().__init__()
        self.photo_dir = "/qt/project_v1/photos"
        self.photos = []  # 照片文件列表
        self.current_index = 0  # 当前查看的照片索引
        self.view_mode = "grid"  # 显示模式：grid(网格) 或 view(查看)
        self.init_ui()
        self.load_photos()
    
    def init_ui(self):
        """初始化UI"""
        # 设置固定大小
        self.setFixedSize(240, 320)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建标题标签
        self.title_label = QLabel("相册")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("WenQuanYi Micro Hei", 16, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #FFD700; background-color: rgba(0,0,0,0.5); padding: 10px; border-radius: 5px;")
        layout.addWidget(self.title_label)
        
        # 创建内容区域（用于切换网格和查看模式）
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_widget)
        
        # 创建网格浏览模式
        self.init_grid_mode()
        
        # 创建查看模式（单张图片查看）
        self.init_view_mode()
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)
        
        # 返回按钮
        self.back_button = QPushButton("←")
        self.back_button.setFixedSize(40, 40)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #D32F2F;
            }
        """)
        self.back_button.clicked.connect(self.on_back)
        button_layout.addWidget(self.back_button)
        
        # 查看按钮
        self.view_button = QPushButton("👁")
        self.view_button.setFixedSize(40, 40)
        self.view_button.setStyleSheet("""
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
        self.view_button.clicked.connect(self.on_view_clicked)
        button_layout.addWidget(self.view_button)
        
        # 上一张按钮
        self.prev_button = QPushButton("◀")
        self.prev_button.setFixedSize(40, 40)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #F57C00;
            }
        """)
        self.prev_button.clicked.connect(self.show_prev_photo)
        button_layout.addWidget(self.prev_button)
        
        # 下一张按钮
        self.next_button = QPushButton("▶")
        self.next_button.setFixedSize(40, 40)
        self.next_button.setStyleSheet("""
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
        self.next_button.clicked.connect(self.show_next_photo)
        button_layout.addWidget(self.next_button)
        
        layout.addLayout(button_layout)
        
        # 设置布局
        self.setLayout(layout)
        
        # 默认显示网格模式
        self.show_grid_mode()
    
    def init_grid_mode(self):
        """初始化网格浏览模式"""
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # 创建网格内容区域
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(5)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置滚动区域的内容
        self.scroll_area.setWidget(self.grid_widget)
    
    def init_view_mode(self):
        """初始化单张查看模式"""
        self.view_widget = QWidget()
        self.view_layout = QVBoxLayout(self.view_widget)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建图片显示标签
        self.photo_display = QLabel()
        self.photo_display.setAlignment(Qt.AlignCenter)
        self.photo_display.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 2px solid #555555;
                color: white;
            }
        """)
        self.photo_display.setFixedSize(200, 150)
        self.view_layout.addWidget(self.photo_display)
        
        # 创建文件名标签
        self.filename_label = QLabel()
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
        self.view_layout.addWidget(self.filename_label)
    
    def load_photos(self):
        """加载照片列表"""
        self.photos = []
        if os.path.exists(self.photo_dir):
            # 获取所有照片文件
            files = os.listdir(self.photo_dir)
            # 过滤出 .jpg 和 .png 文件并按时间排序
            self.photos = sorted([f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))], reverse=True)

        print(f"加载了 {len(self.photos)} 张照片")
        self.refresh_grid()
    
    def refresh_grid(self):
        """刷新网格显示"""
        # 清空现有内容
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.photos:
            # 没有照片时显示提示
            empty_label = QLabel("暂无照片")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #888888; font-size: 14px;")
            self.grid_layout.addWidget(empty_label, 0, 0)
            return
        
        # 添加照片缩略图
        row, col = 0, 0
        for index, photo in enumerate(self.photos):
            # 创建照片容器
            photo_widget = QWidget()
            photo_widget.setFixedSize(65, 65)
            photo_widget.setStyleSheet("""
                QWidget {
                    background-color: #333333;
                    border: 1px solid #555555;
                    border-radius: 3px;
                }
            """)
            
            # 创建照片标签
            photo_label = QLabel(photo_widget)
            photo_label.setGeometry(2, 2, 61, 61)
            photo_label.setAlignment(Qt.AlignCenter)
            photo_label.setStyleSheet("border: none; color: white; font-size: 10px;")
            
            # 加载缩略图
            photo_path = os.path.join(self.photo_dir, photo)
            pixmap = QPixmap(photo_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(61, 61, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                photo_label.setPixmap(scaled_pixmap)
            else:
                photo_label.setText(photo[:8])
            
            # 添加点击事件
            photo_widget.mousePressEvent = lambda event, idx=index: self.show_photo(idx)
            
            # 添加到网格
            self.grid_layout.addWidget(photo_widget, row, col)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def show_grid_mode(self):
        """显示网格模式"""
        self.view_mode = "grid"
        self.title_label.setText("相册")
        
        # 清除内容区域
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # 添加网格视图
        self.content_layout.addWidget(self.scroll_area)
        self.grid_widget.show()
    
    def show_photo(self, index):
        """显示单张照片"""
        if index < 0 or index >= len(self.photos):
            return
        
        self.current_index = index
        self.view_mode = "view"
        
        # 清除内容区域
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # 添加查看视图
        self.content_layout.addWidget(self.view_widget)
        
        # 加载照片
        photo = self.photos[index]
        photo_path = os.path.join(self.photo_dir, photo)
        pixmap = QPixmap(photo_path)
        
        if not pixmap.isNull():
            # 缩放照片以适应显示区域
            scaled_pixmap = pixmap.scaled(196, 146, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_display.setPixmap(scaled_pixmap)
            self.title_label.setText(f"{index + 1}/{len(self.photos)}")
            self.filename_label.setText(photo)
        else:
            self.photo_display.setText("无法加载照片")
    
    def show_next_photo(self):
        """显示下一张照片"""
        if self.view_mode == "view" and self.photos:
            next_index = (self.current_index + 1) % len(self.photos)
            self.show_photo(next_index)
    
    def show_prev_photo(self):
        """显示上一张照片"""
        if self.view_mode == "view" and self.photos:
            prev_index = (self.current_index - 1) % len(self.photos)
            self.show_photo(prev_index)
    
    def on_back(self):
        """返回按钮处理"""
        if self.view_mode == "view":
            # 如果在查看模式，返回网格模式
            self.show_grid_mode()
        else:
            # 如果在网格模式，返回主界面
            self.back_requested.emit()
    
    def on_view_clicked(self):
        """查看按钮处理"""
        if self.view_mode == "grid" and self.photos:
            # 在网格模式，查看第一张照片
            self.show_photo(0)
        elif self.view_mode == "view":
            # 已经在查看模式，不做任何操作
            pass
    
    def handle_key(self, key_code):
        """
        处理按键事件
        
        Args:
            key_code (int): 按键码
        """
        print(f"相册页面按键按下: {key_code}")
        if key_code == 115:  # 按键1 - 查看/确认
            if self.view_mode == "grid" and self.photos:
                print("按键1: 查看当前照片")
                self.show_photo(self.current_index)
            else:
                print("按键1: 无照片可查看")
        elif key_code == 114:  # 按键2 - 返回
            print("按键2: 返回")
            self.on_back()
        elif key_code == 97:  # 按键3 - 下一张
            if self.view_mode == "view":
                print("按键3: 下一张")
                self.show_next_photo()
        elif key_code == 96:  # 按键4 - 上一张
            if self.view_mode == "view":
                print("按键4: 上一张")
                self.show_prev_photo()
    
    def keyPressEvent(self, event):
        """
        按键事件处理
        
        Args:
            event: 按键事件
        """
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 返回键触发返回信号
            self.on_back()
