# WSL2 + ROS2 Humble 环境安装指南

> 目标：WSL 装到 D:\WSL，ROS2 Humble 装在 WSL 内

---

## 📦 概念梳理

### WSL、Ubuntu、ROS2 的关系

```
Windows (C:/D: 盘)
 └─ WSL2（Windows 子系统 Linux，一个轻量虚拟机）
     └─ Ubuntu 22.04（一个 Linux 发行版，跑在 WSL2 里）
         └─ ROS2 Humble（装在 Ubuntu 里的机器人框架，相当于一个软件包集合）
```

| 层 | 是什么 | 装在哪 |
|----|--------|--------|
| **WSL2** | Windows 功能，提供 Linux 运行环境 | 本身在 C 盘（很小，几十 MB） |
| **Ubuntu 22.04** | 一个 Linux 发行版，作为 WSL2 的"实例"运行 | D:\WSL\ext4.vhdx（会随 ROS 安装变大） |
| **ROS2 Humble** | 机器人操作系统，Ubuntu 里 `apt install` 安装的软件 | Ubuntu 内部 `/opt/ros/humble/` |

> 一句话：**WSL2 是容器，Ubuntu 是系统，ROS2 是装在这个系统里的软件。**

### ROS1 vs ROS2

| | ROS1 | ROS2 |
|----|------|------|
| 发布年份 | 2007 | 2017 |
| 最后版本 | Noetic（2020，2025 年停止维护） | 当前 Humble / Iron / Jazzy |
| 通信方式 | TCPROS（自定义协议） | DDS（工业标准） |
| 操作系统 | 仅 Ubuntu | Ubuntu / Windows / macOS |
| 实时性 | 差 | 支持实时控制 |
| 多机器人 | 需要一个 master 节点 | 分布式发现，无中心节点 |
| 嵌入式 | 不太行 | 支持 MCU |
| **选哪个** | 老项目维护 | **新项目一律用 ROS2** |

> 我们用 ROS2 Humble（2022 年发布，LTS 长期支持到 2027 年），跑在 Ubuntu 22.04 上。

---

## 🔧 安装 WSL2 到 D:\WSL

> ⚠️ `--install-location` 实测未生效，实际装到了 C 盘。下面用 **export/import** 搬运到 D 盘。

### 1. 启用 Windows 功能（需管理员 PowerShell）

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```

### 2. 重启电脑

### 3. 更新 WSL 内核

```powershell
wsl --update
```

### 4. 安装 Ubuntu 22.04（默认到 C 盘）

```powershell
wsl --install -d Ubuntu-22.04
```

首次进入会提示创建 Linux 用户名和密码。

### 5. 搬运 Ubuntu 到 D:\WSL

```powershell
# 关机
wsl --shutdown

# 导出到 D 盘
wsl --export Ubuntu-22.04 D:\WSL\ubuntu-22.04.tar

# 注销 C 盘上的
wsl --unregister Ubuntu-22.04

# 导入到 D:\WSL
wsl --import Ubuntu-22.04 D:\WSL D:\WSL\ubuntu-22.04.tar

# 删掉 tar 包（可选，省空间）
Remove-Item D:\WSL\ubuntu-22.04.tar
```

导入后的 vhdx 在 `D:\WSL\ext4.vhdx`。

---

## 🤖 安装 ROS2 Humble

> 💡 **国内用户先换清华源**（否则 apt update 很慢甚至超时）：
> ```bash
> sudo sed -i 's|//.*archive.ubuntu.com|//mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list
> ```

进入 WSL Ubuntu 后，**逐条执行**（方便看进度和定位报错）：

### 1. 基础依赖
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common -y
sudo add-apt-repository universe -y
sudo apt update && sudo apt install curl -y
```

### 2. 添加 ROS2 源
```bash
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

### 3. 安装 ROS2 Humble 桌面版（~2GB，最久）
```bash
sudo apt update && sudo apt install ros-humble-desktop python3-colcon-common-extensions -y
```

### 4. 配置环境
```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 5. 验证
```bash
ros2 topic list
```

---

## 🦾 安装 MoveIt2 + Panda 仿真

```bash
sudo apt install ros-humble-moveit ros-humble-moveit-visual-tools -y
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers -y

mkdir -p ~/robot_ws/src && cd ~/robot_ws
git clone https://github.com/moveit/moveit2_tutorials.git src/moveit2_tutorials -b humble

rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash

# 启动 Panda 仿真
ros2 launch moveit2_tutorials demo.launch.py
```

> ⚠️ `colcon build` 报错缺依赖时，先 `rosdep install --from-paths src --ignore-src -r -y`。
> 
> ⚠️ 国内网络问题：`raw.githubusercontent.com` 连不上就挂代理；ROS 包下载慢可换清华源：
> ```bash
> sudo sed -i 's|http://packages.ros.org|https://mirrors.tuna.tsinghua.edu.cn/ros2|g' /etc/apt/sources.list.d/ros2.list
> ```

---

## 📋 当前进度

| 步骤 | 状态 |
|------|------|
| 创建 D:\WSL 目录 | ✅ 完成 |
| 启用 WSL 功能 | ✅ 完成 |
| 启用虚拟机平台 | ✅ 完成 |
| 重启电脑 | ✅ 完成 |
| 更新 WSL 内核 | ✅ 完成 |
| 安装 Ubuntu 22.04 | ✅ 完成（但装在了 C 盘！） |
| 搬运 Ubuntu 到 D:\WSL | ✅ 完成（vhdx 在 D:\WSL\ext4.vhdx，1.7GB） |
| 安装 ROS2 Humble | ✅ 完成（ros2 topic list 通过） |
| 安装 MoveIt2 apt 包 | ✅ 完成 |
| git clone + 补依赖 + colcon build | ✅ 完成（63s，1 package finished） |
| 启动 Panda 仿真 | ✅ 已验证（WSLg 自带 GUI，xclock 可弹窗） |
