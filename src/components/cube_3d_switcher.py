"""
立方体3D循环切换容器

此文件定义了一个立方体3D循环切换容器，用于展示功能卡片的3D循环效果。

依赖库：
- os：提供文件路径操作
- sys：提供系统相关功能
- math：提供数学计算功能
- PyQt5.QtWidgets：提供GUI组件
- PyQt5.QtGui：提供图像和绘制功能
- PyQt5.QtCore：提供核心功能和动画
"""
import os
import sys
import math
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel,
                             QVBoxLayout, QMessageBox, QStackedWidget)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPainter, QColor, QTransform, QFontDatabase
from PyQt5.QtCore import (Qt, QSize, QPropertyAnimation, QEasingCurve,
                          QTimer, QPoint, pyqtProperty)

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
        # 设置卡片固定尺寸
        self.setFixedSize(200, 200)  # 调整为更适合3D效果的尺寸
        # 获取项目根目录
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
        layout.setContentsMargins(10, 10, 10, 10)  # 适当内边距
        layout.setSpacing(10)  # 适当间距
        
        # 创建标题标签
        self.title_label = QLabel(title)
        # 使用加载的字体或系统默认字体
        font_family = self.custom_font_family if hasattr(self, 'custom_font_family') and self.custom_font_family else "Arial"
        self.title_label.setFont(QFont(font_family, 12, QFont.Bold))  # 字体：自定义或Arial，12号，粗体
        # 设置文本居中对齐
        self.title_label.setAlignment(Qt.AlignCenter)
        # 设置样式
        self.title_label.setStyleSheet("color: #333; padding: 5px 0;")
        # 添加到布局
        layout.addWidget(self.title_label)
        
        # 创建功能按钮
        self.func_btn = QPushButton()
        # 设置按钮样式
        self.func_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: rgba(240, 240, 240, 0.9);
            }
        """)
        
        # 构建图标路径
        icon_path = os.path.join(self.project_root, "assets", "func_icons", icon_name)
        # 检查图标文件是否存在
        if os.path.exists(icon_path):
            # 加载并缩放图标
            icon_pixmap = QPixmap(icon_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # 设置按钮图标
            self.func_btn.setIcon(QIcon(icon_pixmap))
            # 设置图标大小
            self.func_btn.setIconSize(QSize(120, 120))
        # 添加按钮到布局，占据剩余空间
        layout.addWidget(self.func_btn, stretch=1)
        # 绑定按钮点击事件
        self.func_btn.clicked.connect(lambda: self.on_btn_click(title))
        # 设置卡片背景
        self.setStyleSheet("background: rgba(255, 255, 255, 0.95); border-radius: 10px;")

    def on_btn_click(self, func_name):
        """
        按钮点击事件处理
        
        Args:
            func_name (str): 功能名称
        """
        # 显示功能触发消息框
        QMessageBox.information(self, "功能触发", f"进入【{func_name}】功能界面")

class Cube3DSwitcher(QWidget):
    """
    立方体3D循环切换容器
    
    实现功能卡片的3D立方体循环展示效果。
    """
    def __init__(self, parent=None):
        """
        初始化立方体3D切换器
        
        Args:
            parent (QWidget, optional): 父窗口. Defaults to None.
        """
        super().__init__(parent)
        # 设置固定尺寸
        self.setFixedSize(400, 400)  # 调整为更适合展示的尺寸
        # 创建功能卡片
        # 注意：使用album.png代替photo.png，因为photo.png不存在
        self.cards = [
            FuncCard("音乐", "music.png"),
            FuncCard("图片", "album.png"),  # 使用album.png代替photo.png
            FuncCard("相机", "camera.png"),
            FuncCard("视频", "video.png")
        ]
        # 当前旋转角度
        self.current_angle = 0
        # 存储每个卡片的3D位置
        self.card_positions = {}
        # 初始化立方体
        self.init_cube()
        
        # 循环动画
        self.animation = QPropertyAnimation(self, b"rotation")
        self.animation.setDuration(6000)  # 动画时长6秒
        self.animation.setStartValue(0)  # 起始角度0度
        self.animation.setEndValue(360)  # 结束角度360度
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)  # 平滑缓动
        self.animation.setLoopCount(-1)  # 无限循环
        self.animation.start()  # 启动动画

    def init_cube(self):
        """
        初始化立方体
        
        设置4个卡片的初始位置，每个卡片间隔90度。
        """
        # 初始化4个面的立方体位置（前后左右）
        for i, card in enumerate(self.cards):
            card.setParent(self)
            card.hide()  # 初始隐藏，通过paintEvent绘制
            # 每个卡片间隔90度
            self.card_positions[card] = i * 90

    @pyqtProperty(float)
    def rotation(self):
        """
        获取当前旋转角度
        
        Returns:
            float: 当前旋转角度
        """
        return self.current_angle

    @rotation.setter
    def rotation(self, angle):
        """
        设置旋转角度
        
        Args:
            angle (float): 旋转角度
        """
        self.current_angle = angle
        # 触发重绘
        self.update()

    def paintEvent(self, event):
        """
        绘制事件
        
        实现3D立方体效果的绘制。
        
        Args:
            event (QPaintEvent): 绘制事件
        """
        painter = QPainter(self)
        # 设置抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        # 设置平滑像素变换
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 清空背景
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # 立方体中心坐标
        center_x, center_y = self.width() // 2, self.height() // 2
        # 立方体大小
        cube_size = 150
        
        # 按Z轴排序卡片，确保正确的遮挡关系
        sorted_cards = []
        for card, base_angle in self.card_positions.items():
            current_angle = self.current_angle + base_angle
            rad = math.radians(current_angle)
            z = cube_size * math.cos(rad)
            sorted_cards.append((-z, card, current_angle))  # 负号用于降序排序
        
        # 按Z轴深度排序
        sorted_cards.sort()
        
        # 绘制每个卡片
        for _, card, current_angle in sorted_cards:
            # 转换为弧度
            rad = math.radians(current_angle)
            
            # 计算3D位置
            x = center_x + cube_size * math.sin(rad)
            z = cube_size * math.cos(rad)
            
            # 保存当前变换
            painter.save()
            
            # 计算透视缩放因子
            perspective = 800  # 透视强度
            scale = perspective / (perspective + z)
            
            # 平移到卡片位置并应用缩放
            painter.translate(x, center_y)
            painter.scale(scale, scale)
            
            # 距离越远越暗（增强3D感）
            opacity = max(0.3, 1.0 - abs(z) / (cube_size * 1.5))
            painter.setOpacity(opacity)
            
            # 绘制卡片
            card.render(painter, QPoint(-card.width()//2, -card.height()//2))
            
            # 恢复变换
            painter.restore()

if __name__ == "__main__":
    """
    主函数
    
    运行立方体3D循环切换示例。
    """
    # 创建应用程序实例
    app = QApplication(sys.argv)
    # 创建主窗口
    window = QWidget()
    # 设置窗口标题
    window.setWindowTitle("立方体3D循环切换")
    # 设置窗口固定尺寸
    window.setFixedSize(400, 400)
    # 创建垂直布局
    layout = QVBoxLayout(window)
    
    # 创建立方体3D切换器
    switcher = Cube3DSwitcher()
    # 添加到布局
    layout.addWidget(switcher)
    
    # 显示窗口
    window.show()
    # 运行应用程序事件循环
    sys.exit(app.exec_())
