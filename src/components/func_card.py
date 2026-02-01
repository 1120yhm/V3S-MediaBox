"""
功能卡片组件

此文件定义了功能卡片组件，用于在媒体菜单中显示不同的功能选项，如相机、视频、音乐和相册。

依赖库：
- os：提供文件路径操作
- PyQt5.QtWidgets：提供GUI组件
- PyQt5.QtGui：提供图像和字体处理
- PyQt5.QtCore：提供核心功能
"""
import os
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon, QFont, QFontDatabase, QPalette
from PyQt5.QtCore import Qt, QSize

class FuncCard(QWidget):
    """
    功能卡片类
    
    用于显示媒体功能的卡片，包含标签和图标按钮。
    """
    def __init__(self, title, icon_name, parent=None):
        """
        初始化功能卡片
        
        Args:
            title (str): 卡片标题
            icon_name (str): 图标文件名
            parent (QWidget, optional): 父窗口. Defaults to None.
        """
        super().__init__(parent)
        # 设置卡片固定尺寸（调整为适合3D显示的大小）
        self.setFixedSize(160, 160)
        # 获取项目根目录 - 在ARM设备上使用固定路径
        if os.path.exists("/qt/project_v1"):
            self.project_root = "/qt/project_v1"
        else:
            self.project_root = os.getcwd()
        
        # 加载自定义字体
        self.load_custom_fonts()
        
        # 初始化UI
        self.init_ui(title, icon_name)
    
    def load_custom_fonts(self):
        """
        加载自定义字体文件
        """
        # 获取字体文件路径
        font_path = os.path.join(self.project_root, "assets", "fonts", "wqy-microhei.ttc")
        
        # 加载字体到字体数据库
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    self.custom_font_family = font_families[0]
                    print(f"成功加载字体: {self.custom_font_family}")
                else:
                    print("字体加载成功但无法获取字体族名，使用系统默认字体")
                    self.custom_font_family = None
            else:
                print("字体加载失败，使用系统默认字体")
                self.custom_font_family = None
        else:
            print(f"字体文件不存在: {font_path}，使用系统默认字体")
            self.custom_font_family = None

    def init_ui(self, title, icon_name):
        """
        初始化UI组件
        
        Args:
            title (str): 卡片标题
            icon_name (str): 图标文件名
        """
        # 创建垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 无内边距
        layout.setSpacing(0)  # 无间距
        
        # 创建标题标签
        self.title_label = QLabel(title)
        # 使用加载的字体或系统默认字体
        font_family = self.custom_font_family if hasattr(self, 'custom_font_family') and self.custom_font_family else "Arial"
        self.title_label.setFont(QFont(font_family, 9, QFont.Bold))  # 字体：自定义或Arial，9号，粗体
        # 设置文本居中对齐
        self.title_label.setAlignment(Qt.AlignCenter)
        # 设置固定高度
        self.title_label.setFixedHeight(15)
        # 设置样式
        self.title_label.setStyleSheet("color: #333; padding: 1px 0;")
        # 添加到布局
        layout.addWidget(self.title_label)
        
        # 创建功能按钮
        self.func_btn = QPushButton()
        # 设置按钮样式
        self.func_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 0;
                padding: 0;
                margin: 0;
            }
            QPushButton:hover {
                background: rgba(200, 200, 200, 0.5);
            }
        """)
        
        # 构建图标路径
        icon_path = os.path.join(self.project_root, "assets", "func_icons", icon_name)
        # 检查图标文件是否存在
        if os.path.exists(icon_path):
            # 加载并缩放图标（调整为适合卡片大小的尺寸）
            icon_pixmap = QPixmap(icon_path).scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # 设置按钮图标
            self.func_btn.setIcon(QIcon(icon_pixmap))
            # 设置图标大小
            self.func_btn.setIconSize(QSize(140, 140))
        # 添加按钮到布局，占据剩余空间
        layout.addWidget(self.func_btn, stretch=1)
        
        # 设置卡片背景全透明
        self.setStyleSheet("background: rgba(255, 255, 255, 0.0);")

    def on_btn_click(self, func_name):
        """
        按钮点击事件处理
        
        Args:
            func_name (str): 功能名称
        """
        # 显示功能触发消息框
        QMessageBox.information(self, "功能触发", f"进入【{func_name}】功能界面")
