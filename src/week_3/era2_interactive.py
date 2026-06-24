#!/usr/bin/env python3
"""
================================================================================
🎯  Era 2 视觉抓取流水线 — 交互式模拟链路
================================================================================

用法：
  python era2_interactive.py

然后在菜单中：
  [1] 手动输入像素坐标 → 看完整数学变换 → 拿到机器人坐标 → 去 WSL 里手动控制
  [2] 随机生成示例     → 快速了解流程
  [3] 批量演示         → 展示多个不同位置的变换结果
  [4] 逆推             → 输入目标机器人坐标 → 反算需要的像素坐标

输出格式：
  📋 复制以下命令到 WSL 终端运行：
    ros2 topic pub /vla_pose geometry_msgs/PoseStamped "{
      header: {frame_id: 'panda_link0'},
      pose: {position: {x: 0.350, y: 0.100, z: 0.300}, orientation: {w: 1.0}}
    }"
================================================================================
"""

import numpy as np
import math
import time
import random

# ============================================================
# ⚙️  配置参数 (同 era2_pipeline.py)
# ============================================================

CAMERA = {
    "fx": 615.0, "fy": 615.0,   # 焦距 (像素)
    "cx": 320.0, "cy": 240.0,   # 光心 (像素)
    "width": 640, "height": 480,
}

# 相机→机器人基座变换 (T_cam_to_base)
# 相机装在机器人前方 0.25m，高 0.50m，朝下倾斜 30°
CAM_POSE = {
    "tx": 0.25, "ty": 0.0, "tz": 0.50,
    "roll": math.radians(-30),  # 绕 X 轴旋转 -30°
    "pitch": 0.0,
    "yaw": 0.0,
}

# 工作平面高度 (在相机坐标系下的 Z 值)
WORKPLANE_Z = 0.30  # 米

# ============================================================
# 📐  坐标变换引擎 (带详细数学输出)
# ============================================================

class CoordinateTransformer:
    """
    完整 3 步坐标变换，每一步都打印详细数学过程。
    """

    def __init__(self):
        self.cam = CAMERA
        self._build_matrix()

    def _build_matrix(self):
        """构建 T_cam_to_base 4×4 齐次矩阵"""
        rx = CAM_POSE["roll"]
        R = np.array([
            [1, 0, 0],
            [0, math.cos(rx), -math.sin(rx)],
            [0, math.sin(rx),  math.cos(rx)]
        ])
        t = np.array([CAM_POSE["tx"], CAM_POSE["ty"], CAM_POSE["tz"]])
        self.T = np.eye(4)
        self.T[:3, :3] = R
        self.T[:3, 3] = t

    def transform(self, u: float, v: float, verbose: bool = True):
        """
        像素坐标 → 机器人基座坐标 (带详细数学输出)

        参数:
            u, v: 像素坐标
            verbose: 是否打印详细步骤

        返回:
            (x, y, z) 机器人基座坐标系下的 3D 位置
        """
        if verbose:
            print()
            print(f"  {'='*55}")
            print(f"  📐 坐标变换链路")
            print(f"  {'='*55}")
            print(f"  输入: 像素坐标 (u={u:.1f}, v={v:.1f})")
            print()

        # === Step 1: 像素 → 归一化平面 ===
        x_norm = (u - self.cam["cx"]) / self.cam["fx"]
        y_norm = (v - self.cam["cy"]) / self.cam["fy"]

        if verbose:
            print(f"  Step 1: 像素 → 归一化平面")
            print(f"    x_norm = (u - cx) / fx")
            print(f"           = ({u:.1f} - {self.cam['cx']:.1f}) / {self.cam['fx']:.1f}")
            print(f"           = {x_norm:.6f}")
            print(f"    y_norm = (v - cy) / fy")
            print(f"           = ({v:.1f} - {self.cam['cy']:.1f}) / {self.cam['fy']:.1f}")
            print(f"           = {y_norm:.6f}")
            print()

        # === Step 2: 归一化平面 → 相机坐标系 3D ===
        # 假设物体在工作平面上 (Z_cam = WORKPLANE_Z)
        z_cam = WORKPLANE_Z
        x_cam = x_norm * z_cam
        y_cam = y_norm * z_cam

        if verbose:
            print(f"  Step 2: 归一化平面 → 相机坐标系 3D")
            print(f"    假设: 物体在工作平面上 Z_cam = {z_cam:.3f}m")
            print(f"    X_cam = x_norm × Z_cam = {x_norm:.6f} × {z_cam:.3f}")
            print(f"          = {x_cam:.6f} m")
            print(f"    Y_cam = y_norm × Z_cam = {y_norm:.6f} × {z_cam:.3f}")
            print(f"          = {y_cam:.6f} m")
            print(f"    Z_cam = {z_cam:.3f} m")
            print(f"    ─▶ 相机坐标系: ({x_cam:.4f}, {y_cam:.4f}, {z_cam:.4f})")
            print()

        # === Step 3: 相机 → 机器人基座 ===
        P_cam = np.array([x_cam, y_cam, z_cam, 1.0])
        P_base = self.T @ P_cam

        if verbose:
            print(f"  Step 3: 相机坐标系 → 机器人基座坐标系")
            print(f"    T_cam_to_base = Trans({CAM_POSE['tx']}, {CAM_POSE['ty']}, {CAM_POSE['tz']})")
            print(f"                   × RotX({math.degrees(CAM_POSE['roll']):.0f}°)")
            print()
            print(f"    齐次变换矩阵:")
            for row in self.T:
                print(f"      [{row[0]:7.4f}  {row[1]:7.4f}  {row[2]:7.4f}  {row[3]:7.4f}]")
            print()
            print(f"    [X_base]     {self.T[0,0]:7.4f}  {self.T[0,1]:7.4f}  {self.T[0,2]:7.4f}  {self.T[0,3]:7.4f}   [{x_cam:.4f}]")
            print(f"    [Y_base]  =  {self.T[1,0]:7.4f}  {self.T[1,1]:7.4f}  {self.T[1,2]:7.4f}  {self.T[1,3]:7.4f}  ·[{y_cam:.4f}]")
            print(f"    [Z_base]     {self.T[2,0]:7.4f}  {self.T[2,1]:7.4f}  {self.T[2,2]:7.4f}  {self.T[2,3]:7.4f}   [{z_cam:.4f}]")
            print(f"    [  1  ]     {0:7.4f}  {0:7.4f}  {0:7.4f}  {1:7.4f}   [{1:.0f}]")
            print()

        x_base, y_base, z_base = float(P_base[0]), float(P_base[1]), float(P_base[2])

        if verbose:
            print(f"    ─▶ 机器人基座坐标系: ({x_base:.4f}, {y_base:.4f}, {z_base:.4f})")
            print(f"  {'='*55}")
            print()

        return (x_base, y_base, z_base)

    def inverse(self, x: float, y: float, z: float, verbose: bool = True):
        """
        逆变换：机器人基座坐标 → 像素坐标

        用于：你有一个目标抓取位置，想知道它对应图像上哪个像素。

        返回 (u, v) 像素坐标
        """
        T_inv = np.linalg.inv(self.T)
        P_base = np.array([x, y, z, 1.0])
        P_cam = T_inv @ P_base

        x_cam, y_cam, z_cam = P_cam[0], P_cam[1], P_cam[2]

        if verbose:
            print()
            print(f"  {'='*55}")
            print(f"  🔄 逆变换: 机器人坐标 → 像素坐标")
            print(f"  {'='*55}")
            print(f"  输入: 机器人基座 ({x:.4f}, {y:.4f}, {z:.4f})")
            print()
            print(f"  T_base_to_cam = T_cam_to_base⁻¹")
            print()
            for row in T_inv:
                print(f"      [{row[0]:7.4f}  {row[1]:7.4f}  {row[2]:7.4f}  {row[3]:7.4f}]")
            print()
            print(f"  相机坐标系: ({x_cam:.4f}, {y_cam:.4f}, {z_cam:.4f})")
            print()

        # 相机 → 像素
        if z_cam <= 0:
            print("  ❌ 点在相机后方，不可见")
            return None

        u = x_cam / z_cam * self.cam["fx"] + self.cam["cx"]
        v = y_cam / z_cam * self.cam["fy"] + self.cam["cy"]

        if verbose:
            print(f"  u = X_cam / Z_cam × fx + cx")
            print(f"     = {x_cam:.4f} / {z_cam:.4f} × {self.cam['fx']} + {self.cam['cx']}")
            print(f"     = {u:.1f}")
            print(f"  v = Y_cam / Z_cam × fy + cy")
            print(f"     = {y_cam:.4f} / {z_cam:.4f} × {self.cam['fy']} + {self.cam['cy']}")
            print(f"     = {v:.1f}")
            print()
            in_frame = (0 <= u <= self.cam["width"] and 0 <= v <= self.cam["height"])
            print(f"  ─▶ 像素坐标: ({u:.1f}, {v:.1f})  {'✅ 在画面内' if in_frame else '❌ 在画面外'}")
            print(f"  {'='*55}")
            print()

        return (u, v)


# ============================================================
# 🦾  ROS2 命令生成器
# ============================================================

def generate_ros2_command(x, y, z):
    """生成 WSL 中可用的 ROS2 topic pub 命令"""
    cmd = (
        f'ros2 topic pub /vla_pose geometry_msgs/PoseStamped "{{\n'
        f'  header: {{frame_id: \'panda_link0\'}},\n'
        f'  pose: {{position: {{x: {x:.3f}, y: {y:.3f}, z: {z:.3f}}}, orientation: {{w: 1.0}}}}\n'
        f'}}" --once'
    )
    return cmd


def generate_moveit_command(x, y, z):
    """生成 panda_executor.py 中 execute_grasp 方法的坐标"""
    return f'self.moveit2.move_to_pose(position=[{x:.3f}, {y:.3f}, {z:.3f}], quat_xyzw=[0.0, 0.0, 0.0, 1.0], frame_id="panda_link0")'


# ============================================================
# 📋  显示函数
# ============================================================

SHOW_HINT = """
  ┌─────────────────────────────────────────────────────────┐
  │  📋 在 WSL 中运行以下命令验证：                          │
  │                                                         │
  │  1️⃣  Panda 仿真已启动 (终端1):                          │
  │     ros2 launch panda_moveit_config panda_gazebo.launch.py
  │                                                         │
  │  2️⃣  手动控制 Panda (终端2):                            │
  │     ros2 run panda_executor                             │
  │                                                         │
  │  3️⃣  发送抓取指令 (终端3):                              │
"""


def print_header():
    print()
    print("  ╔" + "═" * 53 + "╗")
    print("  ║" + "  🏗️  Era 2 视觉抓取 — 交互式模拟链路".center(43) + "║")
    print("  ╚" + "═" * 53 + "╝")
    print()
    print("  架构:  📷 像素坐标  →  📐 数学变换  →  🦾 WSL 控制")
    print()


def print_menu():
    print()
    print("  ┌──────┬────────────────────────────────────────────┐")
    print("  │ 编号 │ 功能                                      │")
    print("  ├──────┼────────────────────────────────────────────┤")
    print("  │  1   │ 手动输入像素坐标 (u, v) → 完整链路        │")
    print("  │  2   │ 随机生成示例 (快速演示)                     │")
    print("  │  3   │ 批量演示 (3 个不同位置)                    │")
    print("  │  4   │ 逆推: 输入机器人坐标 → 反算像素坐标       │")
    print("  │  5   │ 手眼标定参数查询                           │")
    print("  │  0   │ 退出                                      │")
    print("  └──────┴────────────────────────────────────────────┘")
    print()


# ============================================================
# 🎯  模式实现
# ============================================================

def mode_manual_input(transformer):
    """模式 1: 手动输入像素坐标"""
    print()
    print("  ─── 手动输入像素坐标 ───")
    print(f"  相机分辨率: {CAMERA['width']}×{CAMERA['height']}")
    print(f"  提示: 物体中心在画面内的像素坐标")
    print()

    try:
        u_str = input("  请输入 u (像素列, 0~640) > ").strip()
        v_str = input("  请输入 v (像素行, 0~480) > ").strip()
        u, v = float(u_str), float(v_str)
    except ValueError:
        print("  ❌ 输入格式错误，请输入数字")
        return

    if not (0 <= u <= CAMERA['width'] and 0 <= v <= CAMERA['height']):
        print("  ⚠️  坐标超出画面范围，但计算仍会继续")

    x, y, z = transformer.transform(u, v)

    _print_result(u, v, x, y, z)


def mode_random_demo(transformer):
    """模式 2: 随机生成示例"""
    print()
    print("  ─── 随机生成示例 ───")
    print()

    # 在画面中心附近随机生成像素坐标
    u = CAMERA["cx"] + random.uniform(-150, 150)
    v = CAMERA["cy"] + random.uniform(-80, 80)

    print(f"  🎲 随机像素: (u={u:.1f}, v={v:.1f})")
    print(f"  这模拟了 YOLO 在图像中心附近检测到一个零件。")
    print()

    x, y, z = transformer.transform(u, v)

    _print_result(u, v, x, y, z)


def mode_batch_demo(transformer):
    """模式 3: 批量演示"""
    print()
    print("  ─── 批量演示: 3 个不同位置 ───")
    print()

    test_points = [
        ("🟦  左侧工件", 170, 250),
        ("🟧  中心工件", 320, 260),
        ("🟩  右侧工件", 470, 240),
    ]

    for label, u, v in test_points:
        print(f"  {label}")
        x, y, z = transformer.transform(u, v, verbose=True)
        _print_result(u, v, x, y, z, show_hint=False)
        print()


def mode_inverse(transformer):
    """模式 4: 逆推 — 机器人坐标 → 像素坐标"""
    print()
    print("  ─── 逆推: 机器人坐标 → 像素坐标 ───")
    print("  如果你已经有目标抓取点(比如 WSL 里试出来的)，")
    print("  可以反算它在相机画面里对应哪个像素。")
    print()

    try:
        x_str = input("  请输入 X (米) > ").strip()
        y_str = input("  请输入 Y (米) > ").strip()
        z_str = input("  请输入 Z (米) > ").strip()
        x, y, z = float(x_str), float(y_str), float(z_str)
    except ValueError:
        print("  ❌ 输入格式错误")
        return

    uv = transformer.inverse(x, y, z)
    if uv:
        u, v = uv
        print(f"  📋 结果摘要:")
        print(f"     机器人基座: ({x:.4f}, {y:.4f}, {z:.4f})")
        print(f"     ─▶ 像素:    ({u:.1f}, {v:.1f})")
        print(f"     ─▶ 归一化:  ({(u-CAMERA['cx'])/CAMERA['fx']:.4f}, {(v-CAMERA['cy'])/CAMERA['fy']:.4f})")


def mode_config():
    """模式 5: 查看配置参数"""
    print()
    print("  ─── 手眼标定参数 ───")
    print()
    print(f"  相机内参:")
    print(f"    fx = {CAMERA['fx']:.1f} 像素")
    print(f"    fy = {CAMERA['fy']:.1f} 像素")
    print(f"    cx = {CAMERA['cx']:.1f} 像素  (光心)")
    print(f"    cy = {CAMERA['cy']:.1f} 像素")
    print(f"    分辨率: {CAMERA['width']}×{CAMERA['height']}")
    print()
    print(f"  相机→机器人基座变换:")
    print(f"    平移: x={CAM_POSE['tx']}m, y={CAM_POSE['ty']}m, z={CAM_POSE['tz']}m")
    print(f"    旋转: Roll={math.degrees(CAM_POSE['roll']):.0f}° (朝下)")
    print()
    print(f"  工作平面: Z_cam = {WORKPLANE_Z}m (相机坐标系)")
    print()
    print(f"  适用场景: Panda 工作空间内桌面抓取 (单目 + 已知平面高度)")
    print()


def _print_result(u, v, x, y, z, show_hint=True):
    """打印变换结果和 WSL 命令"""
    print()
    print(f"  ┌{'─'*53}┐")
    print(f"  │ 📋 结果摘要{'':>38}│")
    print(f"  ├{'─'*53}┤")
    print(f"  │ 像素坐标:     (u={u:<7.1f}, v={v:<7.1f}){'':>17}│")
    print(f"  │ 归一化平面:   ({(u-CAMERA['cx'])/CAMERA['fx']:.4f}, {(v-CAMERA['cy'])/CAMERA['fy']:.4f}){'':>21}│")
    print(f"  │ 相机坐标系:   ({x:.4f}, {y:.4f}, {z:.4f}){'':>18}│")
    print(f"  │ 机器人基座:   ({x:.4f}, {y:.4f}, {z:.4f}){'':>18}│")
    print(f"  ├{'─'*53}┤")
    print(f"  │ 🦾 WSL 手动控制命令{'':>32}│")
    print(f"  │{'':>53}│")
    # ROS2 topic pub 命令
    cmd = generate_ros2_command(x, y, z)
    for line in cmd.split('\n'):
        print(f"  │ {line:<51} │")
    print(f"  │{'':>53}│")
    print(f"  │ 或者用 panda_executor 的 execute_grasp:{'':>19}│")
    py_cmd = generate_moveit_command(x, y, z)
    print(f"  │ {py_cmd:<51} │")
    print(f"  └{'─'*53}┘")
    print()

    if show_hint:
        print(f"  💡 在 WSL 中开一个新终端，粘贴上面的 ROS2 命令即可让 Panda 移动到该点。")
        print()


# ============================================================
# 🏃  主循环
# ============================================================

def main():
    transformer = CoordinateTransformer()

    print_header()

    while True:
        print_menu()
        choice = input("  请选择 [0-5] > ").strip()

        if choice == "0":
            print()
            print("  👋 拜拜！去 WSL 里试试吧")
            print()
            break
        elif choice == "1":
            mode_manual_input(transformer)
        elif choice == "2":
            mode_random_demo(transformer)
        elif choice == "3":
            mode_batch_demo(transformer)
        elif choice == "4":
            mode_inverse(transformer)
        elif choice == "5":
            mode_config()
        else:
            print("  ❌ 无效选择，请输入 0-5")


if __name__ == "__main__":
    main()
