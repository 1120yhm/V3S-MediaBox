# V3S 多媒体开发平台

## 项目概述

基于全志 V3S (Lichee Pi Zero) 开发板的多媒体应用平台，集成了相机、视频播放、音乐播放、相册浏览等功能，支持按键控制和触摸屏操作。

## 硬件环境

- **开发板**: Lichee Pi Zero (V3S)
- **处理器**: Allwinner V3s (ARM Cortex-A7 @ 1.2GHz)
- **内存**: 64MB DDR2
- **存储**: 32GB MicroSD
- **显示**: 3.2寸 SPI LCD (ILI9341, 320x240)
- **网络**: 10/100M 以太网
- **音频**: 内置音频 Codec
- **摄像头**: OV2640 (200万像素)

## 软件环境

- **操作系统**: Linux 5.4.31
- **启动方式**: SD 卡启动
- **文件系统**: Buildroot 根文件系统
- **GUI 框架**: PyQt5
- **Python 版本**: 3.x
- **视频播放**: MPlayer
- **音频播放**: Pygame/SDL

## 功能模块

### 1. 主界面
- 实时时间显示（北京时间）
- 天气图标和温度显示
- 功能卡片菜单（相机、视频、音乐、相册）
- 3D 旋转切换动画

### 2. 相机功能
- 实时预览（30fps）
- 拍照保存（/photos/ 目录）
- 视频录制（/videos/ 目录）
- 播放录制的视频

**按键控制**:
- Key1: 拍照
- Key2: 返回
- Key3: 录像/停止
- Key4: 播放视频

### 3. 视频播放
- 支持 MP4、AVI、MKV 等格式
- 全屏播放
- 音量控制
- 播放列表

**按键控制**:
- Key1: 播放/暂停
- Key2: 返回
- Key3: 下一个
- Key4: 上一个

### 4. 音乐播放
- 支持 MP3、WAV、OGG 等格式
- 播放列表管理
- 音量控制
- 播放模式（顺序、随机、单曲循环）

**按键控制**:
- Key1: 播放/暂停
- Key2: 返回
- Key3: 下一个
- Key4: 上一个

### 5. 相册浏览
- 缩略图网格浏览
- 单张图片查看
- 支持 JPG、PNG、BMP、GIF 格式
- 上一张/下一张切换

**按键控制**:
- Key1: 查看
- Key2: 返回
- Key3: 下一张
- Key4: 上一张

## 项目结构

```
project_v1/
├── main.py                 # 程序入口
├── assets/                 # 资源文件
│   ├── fonts/             # 字体文件
│   ├── icons/             # 图标文件
│   ├── images/            # 图片资源
│   └── weather_icons/     # 天气图标
├── music/                  # 音乐文件目录
├── photos/                 # 照片目录
├── videos/                 # 视频目录
└── src/                    # 源代码
    ├── ui/                # UI 界面
    │   ├── main_ui.py     # 主界面
    │   ├── camera_page.py # 相机页面
    │   ├── video_page.py  # 视频页面
    │   ├── music_page.py  # 音乐页面
    │   └── photo_page.py  # 相册页面
    ├── core/              # 核心功能
    │   ├── camera.py      # 相机控制
    │   ├── video_player.py # 视频播放
    │   ├── music_player.py # 音乐播放
    │   └── photo_manager.py # 照片管理
    └── utils/             # 工具类
        ├── key_handler.py    # 按键处理
        ├── arm_key_mapper.py # 按键映射
        └── weather_api.py    # 天气 API
```

## 按键映射

| 按键 | 物理键值 | 功能说明 |
|------|---------|---------|
| Key1 | 115 (0x73) | 确认/拍照/播放 |
| Key2 | 114 (0x72) | 返回/退出 |
| Key3 | 97 (0x61)  | 下一个/录像 |
| Key4 | 96 (0x60)  | 上一个/播放 |

## 启动方式

### SD 卡启动

1. **分区**:
   - 分区1: 32MB FAT32 (boot)
   - 分区2: 剩余空间 ext4 (rootfs)

2. **复制文件**:
   ```bash
   # 内核和设备树 -> 分区1
   cp uImage sun8i-v3s-licheepi-zero.dtb /mnt/sdb1/
   
   # 根文件系统 -> 分区2
   cp -a rootfs/* /mnt/sdb2/
   cp -r project_v1 /mnt/sdb2/qt/
   ```

3. **修改串口配置**:
   ```bash
   sed -i 's/ttySTM0/ttyS0/g' /mnt/sdb2/etc/inittab
   ```

4. **U-Boot 配置**:
   ```bash
   setenv bootcmd 'mmc dev 0; fatload mmc 0:1 0x41000000 uImage; fatload mmc 0:1 0x41c00000 sun8i-v3s-licheepi-zero.dtb; bootm 0x41000000 - 0x41c00000'
   setenv bootargs 'console=ttyS0,115200 root=/dev/mmcblk0p2 rootwait rw'
   saveenv
   ```

### 开机自动启动

创建启动脚本 `/etc/init.d/S99qtapp`:

```bash
#!/bin/sh
cd /qt/project_v1
export QT_QPA_PLATFORM=linuxfb
export QT_QPA_LINUXFB_FB=/dev/fb0
export QT_QPA_EGLFS_HIDECURSOR=1
python3 main.py &
```

```bash
chmod +x /etc/init.d/S99qtapp
```

## 网络配置

### 自动获取 IP (DHCP)

系统启动时自动通过 DHCP 获取 IP 地址。

### 手动配置静态 IP

```bash
ifconfig eth0 192.168.10.153 netmask 255.255.255.0
route add default gw 192.168.10.1
echo "nameserver 114.114.114.114" > /etc/resolv.conf
```

### 测试网络

```bash
ping www.baidu.com
```

## 时间同步

### 设置时区（北京时间）

```bash
export TZ="CST-8"
echo 'export TZ="CST-8"' >> /etc/profile
```

### 手动设置时间

```bash
date -s "2026-01-31 17:40:00"
```

## 内核配置

### 必须启用的驱动

```
CONFIG_MMC=y
CONFIG_MMC_BLOCK=y
CONFIG_MMC_SUNXI=y          # SD卡驱动
CONFIG_EXT4_FS=y            # ext4文件系统
CONFIG_MSDOS_PARTITION=y    # 分区表支持
CONFIG_STMMAC_ETH=y         # 以太网驱动
CONFIG_DWMAC_SUNXI=y
CONFIG_DWMAC_SUN8I=y
CONFIG_USB=y
CONFIG_USB_EHCI_HCD=y
CONFIG_USB_OHCI_HCD=y
```

### 编译内核

```bash
cd ~/v3s/licheepi-linux/linux-5.4.31
make distclean
make ARCH=arm sunxi_defconfig
sed -i 's/# CONFIG_MMC_SUNXI is not set/CONFIG_MMC_SUNXI=y/' .config
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -j12 uImage LOADADDR=0x41000040 dtbs
```

## 常见问题

### 1. SD 卡无法识别

**现象**: `Waiting for root device /dev/mmcblk0p2...`

**解决**: 启用内核配置 `CONFIG_MMC_SUNXI=y`

### 2. 串口登录失败

**现象**: `can't open /dev/ttySTM0`

**解决**: 修改 `/etc/inittab`，将 `ttySTM0` 改为 `ttyS0`

### 3. Qt 程序无法启动

**现象**: 黑屏或报错

**解决**: 设置环境变量
```bash
export QT_QPA_PLATFORM=linuxfb
export QT_QPA_LINUXFB_FB=/dev/fb0
```

### 4. 网络不通

**现象**: ping 不通外网

**解决**: 检查网线连接，确认 DHCP 获取到 IP
```bash
ifconfig eth0
```

## 开发环境

### 主机环境

- Ubuntu 18.04/20.04
- 交叉编译器: arm-linux-gnueabihf-gcc
- Python 3.x
- PyQt5

### 交叉编译

```bash
export ARCH=arm
export CROSS_COMPILE=arm-linux-gnueabihf-
```

## 版本历史

- **V1.0** (2026-01-31)
  - 初始版本
  - 实现相机、视频、音乐、相册功能
  - SD 卡启动支持
  - 网络自动配置
  - 开机自动启动

## 作者

- 开发: AI Assistant & yhm
- 日期: 2026-01-31

## 许可证

MIT License
