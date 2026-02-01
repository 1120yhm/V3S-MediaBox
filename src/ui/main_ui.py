"""
主界面文件

此文件定义了应用程序的主界面，包含天气显示、时间显示和媒体功能菜单。

依赖库：
- os：提供文件路径操作
- PyQt5.QtWidgets：提供GUI组件
- PyQt5.QtGui：提供图像和字体处理
- PyQt5.QtCore：提供核心功能和动画
- src.components.func_card.FuncCard：功能卡片组件
"""
import os
import math
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import (
    QPixmap, QColor, QLinearGradient, QBrush, QIcon, QPalette, QFont, QPainter, QFontDatabase, QKeyEvent
)
from PyQt5.QtCore import (
    Qt, QTimer, QDateTime, QPropertyAnimation, QEasingCurve, QRect, QSize, QPoint, pyqtProperty, pyqtSignal
)
from src.components.func_card import FuncCard

class WeatherMediaUI(QWidget):
    """
    主界面类
    
    包含天气显示、时间显示和媒体功能菜单。
    """
    
    # 定义信号
    camera_selected = pyqtSignal()
    video_selected = pyqtSignal()
    music_selected = pyqtSignal()
    photo_selected = pyqtSignal()
    
    def __init__(self):
        """
        初始化主界面
        """
        super().__init__()
        # 屏幕尺寸：240×320 固定
        self.W = 240
        self.H = 320
        # 当前天气类型
        self.current_weather = "qing"
        # 菜单是否展开
        self.menu_show = False
        # 当前选中的功能卡片索引
        self.current_func_idx = 0
        # 当前3D旋转角度
        self._current_angle = 0
        
        # 初始化按键计时器，用于长按检测
        self.key_press_timer = QTimer(self)
        self.key_press_timer.setSingleShot(True)  # 单次触发
        self.key_press_timer.timeout.connect(self.on_long_key_press)
        self.pressed_key = None  # 当前按下的键
        
        # 加载自定义字体
        self.load_custom_fonts()
        
        # 初始化UI
        self.init_ui()
        # 初始化功能菜单
        self.init_func_menu()
        # 初始化动画
        self.init_animations()
        # 初始化定时器
        self.init_timer()
    
    def load_custom_fonts(self):
        """
        加载自定义字体文件
        """
        # 获取字体文件路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        font_path = os.path.join(project_root, "assets", "fonts", "wqy-microhei.ttc")
        
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

    def init_ui(self):
        """
        初始化UI组件
        
        创建并设置时间区域、天气区域和菜单触发按钮。
        """
        # 设置窗口固定尺寸
        self.setFixedSize(self.W, self.H)
        # 设置无窗口边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # 整体布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 无内边距
        self.main_layout.setSpacing(0)  # 无间距
        
        # 添加顶部占位，将时间和天气往下移动
        top_spacer = QWidget()
        top_spacer.setFixedHeight(90)  # 顶部占位90px（增加10px）
        self.main_layout.addWidget(top_spacer)
        
        # 顶部时间区域
        self.time_widget = QWidget()
        self.time_widget.setFixedHeight(100)  # 固定高度100px
        time_layout = QVBoxLayout(self.time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)  # 无内边距
        time_layout.setSpacing(5)  # 间距5px
        
        # 时间标签
        self.time_label = QLabel(QDateTime.currentDateTime().toString("HH:mm"))
        # 使用加载的字体或系统默认字体
        font_family = self.custom_font_family if hasattr(self, 'custom_font_family') and self.custom_font_family else "Arial"
        self.time_label.setFont(QFont(font_family, 44))  # 字体：自定义或Arial，44号
        self.time_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        self.time_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")  # 白色文本，加粗
        
        # 日期标签
        self.date_label = QLabel(QDateTime.currentDateTime().toString("yyyy-MM-dd"))
        self.date_label.setFont(QFont(font_family, 20))  # 字体：自定义或Arial，20号
        self.date_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        self.date_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")  # 白色文本，加粗
        
        # 添加到时间布局
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.date_label)
        # 添加时间区域到主布局
        self.main_layout.addWidget(self.time_widget)
        
        # 天气区域（水平布局：图标+温度）
        self.weather_widget = QWidget()
        self.weather_widget.setFixedHeight(60)  # 固定高度60px
        weather_layout = QHBoxLayout(self.weather_widget)  # 水平布局
        weather_layout.setContentsMargins(10, 0, 10, 0)  # 左右内边距10px
        weather_layout.setSpacing(10)  # 间距10px
        weather_layout.setAlignment(Qt.AlignCenter)  # 居中对齐
        
        # 天气图标
        self.weather_icon = QLabel()
        # 构建天气图标路径
        icon_path = os.path.join(os.getcwd(), "assets", "icons", "weather", f"{self.current_weather}.png")
        if os.path.exists(icon_path):
            # 加载并缩放图标
            self.weather_icon.setPixmap(QPixmap(icon_path).scaled(50, 50, Qt.KeepAspectRatio))
        self.weather_icon.setAlignment(Qt.AlignCenter)  # 居中对齐
        
        # 温度标签
        self.temp_label = QLabel("25°")
        # 使用加载的字体或系统默认字体
        font_family = self.custom_font_family if hasattr(self, 'custom_font_family') and self.custom_font_family else "Arial"
        self.temp_label.setFont(QFont(font_family, 28, QFont.Bold))  # 字体：自定义或Arial，28号，粗体
        self.temp_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)  # 垂直居中，左对齐
        self.temp_label.setStyleSheet("color: #FFFFFF; font-weight: bold;")  # 白色文本，加粗
        
        # 添加到天气布局（水平排列）
        weather_layout.addWidget(self.weather_icon)
        weather_layout.addWidget(self.temp_label)
        # 添加天气区域到主布局
        self.main_layout.addWidget(self.weather_widget)
        
        # 底部触发按钮 - 完全透明隐藏
        self.trigger_btn = QPushButton("")
        self.trigger_btn.setFixedHeight(20)  # 固定高度20px
        # 设置按钮样式 - 完全透明
        self.trigger_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.0);
                border: none;
                color: rgba(255, 255, 255, 0.0);
                font-size: 1px;
            }
        """)
        # 绑定点击事件
        self.trigger_btn.clicked.connect(self.toggle_menu)
        # 添加到主布局
        self.main_layout.addWidget(self.trigger_btn)
        
        # 设置渐变背景
        self.set_weather_background(self.current_weather)

    def set_weather_background(self, weather_type):
        """
        设置天气背景
        
        根据天气类型设置不同的渐变背景。
        
        Args:
            weather_type (str): 天气类型，可选值：qing, yinpng, yu, xue
        """
        # 尝试使用背景图片
        # 在ARM设备上使用固定路径
        if os.path.exists("/qt/project_v1"):
            project_root = "/qt/project_v1"
        else:
            project_root = os.getcwd()
            
        # 构建背景图片路径
        bg_path = os.path.join(project_root, "assets", "images", "logo1.ppm")
        
        # 检查背景图片文件是否存在
        if os.path.exists(bg_path):
            # 加载背景图片
            bg_pixmap = QPixmap(bg_path)
            if bg_pixmap.isNull():
                print(f"无法加载背景图片: {bg_path}")
                # 使用渐变背景
                self._set_gradient_background(weather_type)
                return
                
            # 缩放图片以适应窗口大小
            scaled_pixmap = bg_pixmap.scaled(self.W, self.H, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            
            # 使用QPalette设置背景
            palette = self.palette()
            palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
            print(f"成功设置背景图片: {bg_path}，大小: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
        else:
            # 如果背景图片不存在，使用渐变背景
            self._set_gradient_background(weather_type)
            print(f"背景图片不存在: {bg_path}，使用渐变背景")
    
    def _set_gradient_background(self, weather_type):
        """
        设置渐变背景
        
        Args:
            weather_type (str): 天气类型，可选值：qing, yinpng, yu, xue
        """
        # 创建线性渐变
        gradient = QLinearGradient(0, 0, 0, self.H)
        # 根据天气类型设置不同的渐变颜色
        if weather_type == "qing":  # 晴天
            gradient.setColorAt(0, QColor(255, 245, 230))
            gradient.setColorAt(1, QColor(255, 220, 180))
        elif weather_type == "yinpng":  # 阴天
            gradient.setColorAt(0, QColor(230, 235, 240))
            gradient.setColorAt(1, QColor(200, 205, 210))
        elif weather_type == "yu":  # 雨天
            gradient.setColorAt(0, QColor(220, 235, 245))
            gradient.setColorAt(1, QColor(180, 210, 230))
        elif weather_type == "xue":  # 雪天
            gradient.setColorAt(0, QColor(240, 245, 250))
            gradient.setColorAt(1, QColor(210, 220, 230))
        
        # 设置窗口背景
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def init_func_menu(self):
        """
        初始化功能菜单
        
        创建菜单容器和功能卡片，实现3D切换效果。
        """
        # 菜单容器
        self.menu_widget = QWidget(self)
        self.menu_widget.setFixedSize(self.W, 265)  # 固定尺寸：240×265
        # 设置菜单样式 - 全透明背景
        self.menu_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.0);
            }
        """)
        # 初始位置：屏幕外
        self.menu_widget.setGeometry(QRect(0, self.H, self.W, 265))
        
        # 创建功能卡片
        self.camera_card = FuncCard("Music", "music.png")  # 相机卡片（显示Music）
        self.video_card = FuncCard("Video", "video.png")  # 视频卡片
        self.music_card = FuncCard("Camera", "camera.png")  # 音乐卡片（显示Camera）
        self.album_card = FuncCard("Album", "album.png")  # 相册卡片
        
        # 将卡片添加到菜单容器
        self.cards = [self.camera_card, self.video_card, self.music_card, self.album_card]
        for i, card in enumerate(self.cards):
            card.setParent(self.menu_widget)
            card.hide()  # 初始隐藏，通过paintEvent绘制
            
        # 存储每个卡片的3D位置
        self.card_positions = {}
        for i, card in enumerate(self.cards):
            # 每个卡片间隔90度
            self.card_positions[card] = i * 90
        
        # 设置焦点策略，捕获物理按键
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 为菜单容器添加paintEvent方法
        # 保存WeatherMediaUI实例的引用
        weather_media_ui = self
        
        def menu_paint_event(event):
            painter = QPainter(weather_media_ui.menu_widget)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            # 清空背景 - 全透明
            painter.fillRect(weather_media_ui.menu_widget.rect(), QColor(255, 255, 255, 0))  # 完全透明背景
            
            # 立方体中心坐标
            center_x, center_y = weather_media_ui.menu_widget.width() // 2, weather_media_ui.menu_widget.height() // 2
            # 立方体大小（卡片宽度的一半）
            cube_size = weather_media_ui.cards[0].width() // 2
            
            # 按Z轴排序卡片，确保正确的遮挡关系
            sorted_cards = []
            for card, base_angle in weather_media_ui.card_positions.items():
                current_angle = weather_media_ui.current_angle + base_angle
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
                perspective = 500  # 透视强度
                scale = perspective / (perspective + z)
                
                # 平移到卡片位置并应用缩放
                painter.translate(x, center_y)
                painter.scale(scale, scale)
                
                # 不设置透明度，保持原始状态
                
                # 绘制卡片的标题
                title_rect = QRect(-card.width()//2, -card.height()//2, card.width(), 15)
                painter.drawText(title_rect, Qt.AlignCenter, card.title_label.text())
                
                # 直接绘制图标，不绘制按钮背景
                icon_rect = QRect(-card.width()//2, -card.height()//2 + 15, card.width(), card.height() - 15)
                # 检查功能按钮是否有图标
                if card.func_btn.icon():
                    icon = card.func_btn.icon()
                    icon.paint(painter, icon_rect, Qt.AlignCenter)
                
                # 恢复变换
                painter.restore()
        
        # 替换菜单容器的paintEvent方法
        self.menu_widget.paintEvent = menu_paint_event
        # 强制重绘
        self.menu_widget.update()

    def keyPressEvent(self, event):
        """
        键盘事件处理
        
        处理物理按键事件，映射到卡片选择和确认功能。
        
        物理按键映射：
        - 按键1 (上键)：展开菜单
        - 按键2 (下键)：收起菜单
        - 按键3 (左键)：切换到上一张卡片
        - 按键4 (右键)：切换到下一张卡片
        - 长按任意键：确认选择当前卡片
        
        ARM设备特殊按键码处理：
        - 直接处理原始按键码
        
        Args:
            event (QKeyEvent): 键盘事件
        """
        # 记录按下的键
        self.pressed_key = event.key()
        
        # 添加调试信息
        print(f"按键事件: key={event.key()}, text='{event.text()}'")
        
        # 启动长按检测计时器（1秒后触发）
        self.key_press_timer.start(1000)
        
        # 直接处理按键事件
        if self.menu_show:
            # 菜单展开状态
            if event.key() == Qt.Key_Left:
                # 左键：切换到上一张卡片
                self.switch_func_card(-1)
            elif event.key() == Qt.Key_Right:
                # 右键：切换到下一张卡片
                self.switch_func_card(1)
            elif event.key() == Qt.Key_Down:
                # 下键：收起菜单
                self.toggle_menu()
            # 添加ARM设备按键码的直接处理
            elif event.key() == 115:  # 按键1 (0x73)
                # 上键：在菜单展开状态下不做特殊操作
                pass
            elif event.key() == 114:  # 按键2 (0x72)
                # 下键：收起菜单
                self.toggle_menu()
            elif event.key() == 97:   # 按键3 (0x61)
                # 左键：切换到上一张卡片
                self.switch_func_card(-1)
            elif event.key() == 96:   # 按键4 (0x60)
                # 右键：切换到下一张卡片
                self.switch_func_card(1)
        else:
            # 菜单收起状态
            if event.key() == Qt.Key_Up:
                # 上键：展开菜单
                self.toggle_menu()
            # 添加ARM设备按键码的直接处理
            elif event.key() == 115:  # 按键1 (0x73)
                # 上键：展开菜单
                self.toggle_menu()
        # 调用父类方法
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """
        按键释放事件处理
        
        停止长按检测计时器
        
        Args:
            event (QKeyEvent): 按键事件
        """
        # 停止长按检测计时器
        self.key_press_timer.stop()
        self.pressed_key = None
        # 调用父类方法
        super().keyReleaseEvent(event)
    
    def handle_key_release(self, key_code):
        """
        处理原始按键释放事件
        
        停止长按检测计时器
        
        Args:
            key_code (int): 原始按键码
        """
        print(f"处理按键释放: {key_code}")
        # 停止长按检测计时器
        self.key_press_timer.stop()
        self.pressed_key = None
    
    def handle_raw_key_code(self, key_code):
        """
        处理原始按键码
        
        直接处理来自输入设备的原始按键码。
        
        Args:
            key_code (int): 原始按键码
        """
        print(f"处理原始按键码: {key_code}")
        
        # 更新当前按下的键，用于长按检测
        self.pressed_key = key_code
        # 启动长按检测计时器（1秒后触发）
        self.key_press_timer.start(1000)
        
        # 无论菜单状态如何，都处理所有按键
        # 使用独立的if语句，确保所有按键都能被检查
        if key_code == 115:  # 按键1 (0x73)
            # 展开菜单（如果菜单未展开）
            if not self.menu_show:
                print("按键1：展开菜单")
                self.toggle_menu()
        
        if key_code == 114:  # 按键2 (0x72)
            # 收起菜单（如果菜单已展开）
            if self.menu_show:
                print("按键2：收起菜单")
                self.toggle_menu()
        
        if key_code == 97:  # 按键3 (0x61)
            # 切换到上一张卡片（如果菜单已展开）
            if self.menu_show:
                print("按键3：切换到上一张卡片")
                self.switch_func_card(-1)
        
        if key_code == 96:  # 按键4 (0x60)
            # 切换到下一张卡片（如果菜单已展开）
            if self.menu_show:
                print("按键4：切换到下一张卡片")
                self.switch_func_card(1)

    def on_long_key_press(self):
        """
        长按按键处理
        
        当按键长按1秒后触发，根据按键执行不同功能：
        - 按键1：确认选择当前卡片
        - 按键2：退出应用程序
        """
        if self.pressed_key is not None:
            if self.menu_show and self.pressed_key == 115:  # 按键1 (0x73)
                # 菜单展开状态下长按按键1确认选择当前卡片
                print("长按按键1：确认选择")
                self.confirm_current_card()
            elif self.pressed_key == 114:  # 按键2 (0x72)
                # 长按按键2退出应用程序
                from PyQt5.QtWidgets import QApplication
                print("长按按键2：退出应用")
                QApplication.quit()

    def switch_func_card(self, direction):
        """
        切换功能卡片
        
        实现卡片之间的3D旋转切换动画。
        
        Args:
            direction (int): 切换方向，-1表示向左，1表示向右
        """
        # 计算新卡片索引
        new_idx = self.current_func_idx + direction
        if new_idx < 0:
            # 索引越界，循环到最后一张
            new_idx = len(self.cards) - 1
        elif new_idx >= len(self.cards):
            # 索引越界，循环到第一张
            new_idx = 0
        
        # 计算旋转角度（90度为一个卡片）
        angle_change = direction * 90
        start_angle = self.current_angle
        end_angle = self.current_angle + angle_change
        
        # 动画参数 - 直接修改这里调整速度
        duration = 300  # 动画时长300ms（更快）
        frames = 20  # 减少帧数使动画更快
        frame_duration = duration / frames
        angle_step = angle_change / frames
        
        # 创建动画定时器
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(int(frame_duration))
        
        # 使用类变量存储动画状态
        self.anim_frame_count = 0
        self.anim_frames = frames
        self.anim_start_angle = start_angle
        self.anim_angle_step = angle_step
        self.anim_new_idx = new_idx
        
        # 动画更新函数
        def update_animation():
            self.anim_frame_count += 1
            
            # 计算当前角度（使用缓动函数）
            t = self.anim_frame_count / self.anim_frames
            # 使用简单的缓动函数
            eased_t = t * t * (3 - 2 * t)  # InOutQuad
            current_angle = self.anim_start_angle + self.anim_angle_step * self.anim_frame_count * eased_t
            
            # 更新角度
            self.current_angle = current_angle
            
            # 触发重绘
            self.menu_widget.update()
            
            # 检查动画是否结束
            if self.anim_frame_count >= self.anim_frames:
                # 动画结束，更新索引
                self.current_func_idx = self.anim_new_idx
                # 确保角度在0-360范围内
                self.current_angle %= 360
                # 停止定时器
                self.anim_timer.stop()
        
        # 连接信号并启动
        self.anim_timer.timeout.connect(update_animation)
        self.anim_timer.start()
        
        # 触发初始重绘
        self.menu_widget.update()

    def init_animations(self):
        """
        初始化动画
        
        创建菜单展开/收起的动画。
        """
        # 创建菜单动画
        self.menu_anim = QPropertyAnimation(self.menu_widget, b"geometry")
        self.menu_anim.setDuration(350)  # 动画时长350ms
        self.menu_anim.setEasingCurve(QEasingCurve.OutCubic)  # 缓动曲线

    @pyqtProperty(float)
    def current_angle(self):
        """
        获取当前3D旋转角度
        
        Returns:
            float: 当前旋转角度
        """
        return self._current_angle

    @current_angle.setter
    def current_angle(self, angle):
        """
        设置当前3D旋转角度
        
        Args:
            angle (float): 旋转角度
        """
        self._current_angle = angle
        # 触发菜单容器重绘
        if hasattr(self, 'menu_widget'):
            self.menu_widget.update()

    def toggle_menu(self):
        """
        展开/收起菜单
        
        实现菜单的平滑展开和收起动画。
        """
        if not self.menu_show:
            # 展开菜单
            # 开始位置：屏幕底部
            self.menu_anim.setStartValue(QRect(0, self.H, self.W, 265))
            # 结束位置：顶部（时间区域下方）
            self.menu_anim.setEndValue(QRect(0, 55, self.W, 265))  # 调整Y坐标为55px
            # 更新菜单状态
            self.menu_show = True
        else:
            # 收起菜单
            # 开始位置：顶部（时间区域下方）
            self.menu_anim.setStartValue(QRect(0, 55, self.W, 265))
            # 结束位置：屏幕底部
            self.menu_anim.setEndValue(QRect(0, self.H, self.W, 265))
            # 更新菜单状态
            self.menu_show = False
        # 开始动画
        self.menu_anim.start()

    def confirm_current_card(self):
        """
        确认选择当前卡片
        
        执行当前选中卡片的功能。
        """
        if self.menu_show and 0 <= self.current_func_idx < len(self.cards):
            # 获取当前选中的卡片
            current_card = self.cards[self.current_func_idx]
            # 获取卡片标题
            card_title = current_card.title_label.text()
            # 打印调试信息
            print(f"确认卡片: 索引={self.current_func_idx}, 标题={card_title}")
            # 发射相应的信号（注意：卡片显示和实际功能已交换）
            if card_title == "Music":
                print("发射 camera_selected 信号（显示Music卡片，实际是相机功能）")
                self.camera_selected.emit()
            elif card_title == "Video":
                print("发射 video_selected 信号")
                self.video_selected.emit()
            elif card_title == "Camera":
                print("发射 music_selected 信号（显示Camera卡片，实际是音乐功能）")
                self.music_selected.emit()
            elif card_title == "Album":
                print("发射 photo_selected 信号")
                self.photo_selected.emit()
    
    def execute_card_function(self, func_name):
        """
        执行卡片功能
        
        根据功能名称执行相应的操作。
        
        Args:
            func_name (str): 功能名称
        """
        if func_name == "相机":
            QMessageBox.information(self, "功能启动", "相机功能已启动")
        elif func_name == "视频":
            QMessageBox.information(self, "功能启动", "视频功能已启动")
        elif func_name == "音乐":
            QMessageBox.information(self, "功能启动", "音乐功能已启动")
        elif func_name == "相册":
            QMessageBox.information(self, "功能启动", "相册功能已启动")
        else:
            QMessageBox.information(self, "功能启动", f"未知功能: {func_name}")

    def init_timer(self):
        """
        初始化定时器
        
        创建时间更新和天气获取的定时器。
        """
        # 时间更新定时器
        self.time_timer = QTimer(self)
        self.time_timer.setInterval(1000)  # 间隔1000ms
        self.time_timer.timeout.connect(self.update_time)  # 绑定超时事件
        self.time_timer.start()  # 启动定时器
        
        # 天气更新定时器
        self.weather_timer = QTimer(self)
        self.weather_timer.setInterval(300000)  # 间隔5分钟(300000ms)
        self.weather_timer.timeout.connect(self.update_weather)  # 绑定超时事件
        self.weather_timer.start()  # 启动定时器
        
        # 初始更新天气
        self.update_weather()

    def update_time(self):
        """
        更新时间
        
        实时更新时间和日期显示。
        """
        # 获取当前时间并加上8小时（北京时间 = UTC+8）
        current_time = QDateTime.currentDateTime()
        beijing_time = current_time.addSecs(8 * 3600)  # 加8小时
        
        # 更新时间标签
        self.time_label.setText(beijing_time.toString("HH:mm"))
        # 更新日期标签
        self.date_label.setText(beijing_time.toString("yyyy-MM-dd"))

    def update_weather(self):
        """
        更新天气信息
        
        从天气API获取最新天气数据。
        """
        try:
            # 导入天气API
            from src.utils.weather_api import WeatherAPI
            # 创建天气API实例
            weather_api = WeatherAPI()
            # 获取天气信息
            weather_info = weather_api.get_weather()
            # 解析天气信息
            if "°" in weather_info:
                # 提取温度
                temp_str = weather_info.split("温度：")[1].split("℃")[0].strip()
                self.temp_label.setText(f"{temp_str}°")
            
            # 根据天气信息设置天气类型
            if "晴" in weather_info:
                self.current_weather = "qing"
            elif "阴" in weather_info:
                self.current_weather = "yinpng"
            elif "雨" in weather_info:
                self.current_weather = "yu"
            elif "雪" in weather_info:
                self.current_weather = "xue"
            
            # 更新天气图标
            icon_path = os.path.join(os.getcwd(), "assets", "icons", "weather", f"{self.current_weather}.png")
            if os.path.exists(icon_path):
                # 加载并缩放图标
                self.weather_icon.setPixmap(QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio))
            
            # 更新背景
            self.set_weather_background(self.current_weather)
            print(f"天气更新: {weather_info}")
        except Exception as e:
            print(f"天气更新失败: {e}")

    def simulate_weather_change(self):
        """
        模拟天气变化
        
        循环切换天气类型，更新天气显示和背景。
        """
        # 天气类型列表
        weather_list = ["qing", "yinpng", "yu", "xue"]
        # 获取当前天气索引
        idx = weather_list.index(self.current_weather)
        # 切换到下一个天气类型
        self.current_weather = weather_list[(idx + 1) % 4]
        
        # 构建天气图标路径
        icon_path = os.path.join(os.getcwd(), "assets", "icons", "weather", f"{self.current_weather}.png")
        if os.path.exists(icon_path):
            # 加载并缩放图标
            self.weather_icon.setPixmap(QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio))
        # 更新温度显示
        self.temp_label.setText(f"{18 + idx * 2}℃")
        # 更新天气背景
        self.set_weather_background(self.current_weather)
