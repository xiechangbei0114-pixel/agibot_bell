#!/usr/bin/env python3
"""
fk_ik_simulator.py — FK/IK 纯 Python 仿真（无需 ROS2 / GPU）

功能：
  1. 2 连杆机械臂 FK/IK 可视化（matplotlib 动画）
  2. 5 自由度机械臂数值 IK（Jacobian 伪逆法）
  3. 展示"多解"、"无解"、"奇异位姿"三个核心概念

用法：
  pip install numpy matplotlib
  python fk_ik_simulator.py

面试话术：「我写过一个 FK/IK 仿真，演示了多解/无解/奇异——这些就是 VLA
            翻车时底层到底发生了什么。」
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import matplotlib.animation as animation
from dataclasses import dataclass
from typing import Optional, List, Tuple


# ============================================================
# Part 1: 2-Link 机械臂 FK/IK（可视化核心）
# ============================================================

@dataclass
class TwoLinkArm:
    """2 连杆机械臂"""
    l1: float = 1.0   # 大臂长度
    l2: float = 0.8   # 小臂长度

    def fk(self, theta1: float, theta2: float) -> Tuple[float, float]:
        """正运动学：关节角 → 末端位置"""
        x = self.l1 * np.cos(theta1) + self.l2 * np.cos(theta1 + theta2)
        y = self.l1 * np.sin(theta1) + self.l2 * np.sin(theta1 + theta2)
        return x, y

    def ik(self, x: float, y: float, elbow_up: bool = True) -> Optional[Tuple[float, float, float, float]]:
        """
        逆运动学：末端位置 → 关节角（解析解）
        返回 (theta1, theta2, theta1_alt, theta2_alt) 两组解，或 None（无解）
        """
        # 计算可达性
        d2 = x**2 + y**2
        max_reach = self.l1 + self.l2
        min_reach = abs(self.l1 - self.l2)

        if d2 > max_reach**2 or d2 < min_reach**2:
            return None  # 无解

        cos_theta2 = (d2 - self.l1**2 - self.l2**2) / (2 * self.l1 * self.l2)
        cos_theta2 = np.clip(cos_theta2, -1.0, 1.0)

        # 肘关节：两组解（朝上 / 朝下）
        theta2_up = np.arccos(cos_theta2)     # 肘朝上
        theta2_down = -theta2_up               # 肘朝下

        def solve_for_theta1(theta2_val: float) -> float:
            k1 = self.l1 + self.l2 * np.cos(theta2_val)
            k2 = self.l2 * np.sin(theta2_val)
            return np.arctan2(y, x) - np.arctan2(k2, k1)

        theta1_up = solve_for_theta1(theta2_up)
        theta1_down = solve_for_theta1(theta2_down)

        if elbow_up:
            return (theta1_up, theta2_up, theta1_down, theta2_down)
        else:
            return (theta1_down, theta2_down, theta1_up, theta2_up)

    def get_arm_points(self, theta1: float, theta2: float) -> Tuple[float, float, float, float]:
        """获取机械臂可视化的两个线段端点"""
        j1_x = self.l1 * np.cos(theta1)
        j1_y = self.l1 * np.sin(theta1)
        ee_x, ee_y = self.fk(theta1, theta2)
        return 0, 0, j1_x, j1_y, ee_x, ee_y


# ============================================================
# Part 2: 5-DOF 机械臂数值 IK（Jacobian 伪逆法）
# ============================================================

class NumericalIK:
    """
    数值 IK 求解器 — Jacobian 伪逆法 (DLS)
    展示"冗余自由度"和"奇异位姿"概念
    """

    def __init__(self, link_lengths: List[float]):
        self.links = link_lengths  # 各连杆长度
        self.n_joints = len(link_lengths)

    def fk_5dof(self, joint_angles: np.ndarray) -> Tuple[float, float]:
        """5-DOF 正运动学"""
        x, y = 0.0, 0.0
        angle_sum = 0.0
        for i in range(self.n_joints):
            angle_sum += joint_angles[i]
            x += self.links[i] * np.cos(angle_sum)
            y += self.links[i] * np.sin(angle_sum)
        return x, y

    def jacobian_5dof(self, joint_angles: np.ndarray) -> np.ndarray:
        """计算 2×n 雅可比矩阵"""
        J = np.zeros((2, self.n_joints))
        angle_sum = 0.0
        for i in range(self.n_joints):
            angle_sum += joint_angles[i]
            J[0, i] = -np.sin(angle_sum)
            J[1, i] = np.cos(angle_sum)
        # 考虑连杆长度
        for j in range(self.n_joints):
            for k in range(j, self.n_joints):
                angle_sum_k = np.sum(joint_angles[:k+1])
                J[0, j] *= self.links[j]
                J[1, j] *= self.links[j]
                if k > j:
                    J[0, j] += self.links[k] * -np.sin(angle_sum_k)
                    J[1, j] += self.links[k] * np.cos(angle_sum_k)
        return J

    def ik_solve(self, target_x: float, target_y: float,
                 init_angles: Optional[np.ndarray] = None,
                 max_iter: int = 100, tol: float = 1e-4,
                 damping: float = 0.1) -> Tuple[bool, np.ndarray, List[float]]:
        """
        阻尼最小二乘法 (DLS) 数值 IK
        返回 (收敛?, 关节角, 误差历史)
        """
        if init_angles is None:
            angles = np.zeros(self.n_joints)
        else:
            angles = init_angles.copy()

        errors = []
        for _ in range(max_iter):
            ee_x, ee_y = self.fk_5dof(angles)
            dx = target_x - ee_x
            dy = target_y - ee_y
            error = np.sqrt(dx**2 + dy**2)
            errors.append(error)

            if error < tol:
                return True, angles, errors

            J = self.jacobian_5dof(angles)
            # DLS: J^T (J J^T + λ² I)^{-1}
            Jt = J.T
            JJt = J @ Jt
            lambda_sq = damping ** 2
            delta = Jt @ np.linalg.solve(JJt + lambda_sq * np.eye(2), np.array([dx, dy]))
            angles += delta

        return False, angles, errors


# ============================================================
# Part 3: 可视化演示
# ============================================================

def demo_two_link_arm():
    """2 连杆 FK/IK 交互演示"""
    arm = TwoLinkArm()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # --- 左图：双解演示 ---
    ax1.set_title("2 连杆 IK 双解：肘朝上 vs 肘朝下", fontsize=12)
    ax1.set_xlim(-1.8, 1.8)
    ax1.set_ylim(-1.8, 1.8)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)
    target = (0.6, 1.2)
    ax1.plot(*target, 'r*', markersize=15, label='目标位置')

    # 肘朝上
    sol = arm.ik(target[0], target[1], elbow_up=True)
    if sol:
        t1_up, t2_up, _, _ = sol
        _, _, jx, jy, eex, eey = arm.get_arm_points(t1_up, t2_up)
        ax1.plot([0, jx], [0, jy], 'b-o', linewidth=3, label='肘朝上: 大臂')
        ax1.plot([jx, eex], [jy, eey], 'b--o', linewidth=3, label='肘朝上: 小臂')
        ax1.plot(eex, eey, 'bo', markersize=8)

    # 肘朝下
    sol = arm.ik(target[0], target[1], elbow_up=False)
    if sol:
        t1_down, t2_down, _, _ = sol
        _, _, jx, jy, eex, eey = arm.get_arm_points(t1_down, t2_down)
        ax1.plot([0, jx], [0, jy], 'g-o', linewidth=2, label='肘朝下: 大臂')
        ax1.plot([jx, eex], [jy, eey], 'g--o', linewidth=2, label='肘朝下: 小臂')
        ax1.plot(eex, eey, 'go', markersize=8)

    ax1.legend(fontsize=9)
    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')

    # --- 右图：可达空间 ---
    ax2.set_title("2 连杆可达空间 (Workspace)", fontsize=12)
    ax2.set_xlim(-1.8, 1.8)
    ax2.set_ylim(-1.8, 1.8)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)

    # 蒙特卡洛采样可达空间
    np.random.seed(42)
    points = []
    for _ in range(2000):
        t1 = np.random.uniform(-np.pi, np.pi)
        t2 = np.random.uniform(-np.pi, np.pi)
        x, y = arm.fk(t1, t2)
        points.append((x, y))
    xs, ys = zip(*points)
    ax2.scatter(xs, ys, s=1, alpha=0.3, c='blue', label='可达区域')

    # 标注不可达点
    unreachable = [(1.5, 1.5), (-1.5, 0.0), (0.0, -2.0)]
    for ux, uy in unreachable:
        ax2.plot(ux, uy, 'rx', markersize=12, mew=3)
        ax2.annotate(f'不可达\n({ux},{uy})', (ux, uy),
                     xytext=(5, 5), textcoords='offset points', fontsize=9, color='red')

    # 外边界
    theta = np.linspace(0, 2*np.pi, 100)
    outer = arm.l1 + arm.l2
    ax2.plot(outer*np.cos(theta), outer*np.sin(theta), 'r--', alpha=0.5, label='最大可达边界')
    inner = abs(arm.l1 - arm.l2)
    if inner > 0.01:
        ax2.plot(inner*np.cos(theta), inner*np.sin(theta), 'r--', alpha=0.3, label='最小可达边界')

    ax2.legend(fontsize=9)
    ax2.set_xlabel('X (m)')

    plt.suptitle('FK/IK 核心概念演示 — 面试现场可画', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()


def demo_numerical_ik():
    """5-DOF 数值 IK 演示——奇异位姿"""
    print("=" * 60)
    print("5-DOF 机械臂数值 IK 演示（Jacobian 伪逆法）")
    print("=" * 60)

    arm = NumericalIK([0.5, 0.4, 0.3, 0.2, 0.1])

    # 正常情况
    target = (1.2, 0.5)
    init = np.array([0.5, 0.3, -0.2, 0.1, 0.0])
    success, angles, errors = arm.ik_solve(target[0], target[1], init_angles=init)

    print(f"\n📍 目标位置: ({target[0]}, {target[1]})")
    print(f"{'✅ 收敛' if success else '❌ 未收敛'}")
    print(f"关节角: {np.round(angles, 3)}")
    ee_x, ee_y = arm.fk_5dof(angles)
    print(f"末端位置: ({ee_x:.4f}, {ee_y:.4f})")
    print(f"最终误差: {errors[-1]:.6f}")
    print(f"迭代次数: {len(errors)}")

    # 奇异情况：手臂完全伸直
    print(f"\n{'='*60}")
    print("奇异位姿测试：手臂完全伸直（自由度降级）")
    singular_angles = np.zeros(5)  # 全部 0 → 伸直
    ee_x, ee_y = arm.fk_5dof(singular_angles)
    print(f"伸直时末端: ({ee_x:.4f}, {ee_y:.4f})")

    # 尝试从奇异位姿微调
    target_near = (ee_x + 0.01, ee_y + 0.01)
    success, angles_s, errors_s = arm.ik_solve(
        target_near[0], target_near[1],
        init_angles=singular_angles,
        damping=0.5  # 奇异时加大阻尼
    )

    print(f"目标: ({target_near[0]}, {target_near[1]})")
    print(f"{'✅ 收敛（加大阻尼后）' if success else '❌ 未收敛（奇异导致）'}")
    print(f"关节角变化: {np.round(angles_s - singular_angles, 4)}")
    print("→ 观察：奇异时关节角剧烈变化才能让末端移动一小点")
    print("→ 面试话术：'这就是 VLA 翻车时底层发生的事——奇异导致 IK 不稳定'")

    # 不可达测试
    print(f"\n{'='*60}")
    print("不可达测试：目标太远")
    far_target = (10.0, 10.0)
    success, _, errors_far = arm.ik_solve(far_target[0], far_target[1], init_angles=init)
    print(f"目标: ({far_target[0]}, {far_target[1]})")
    print(f"{'⚠️ 正常收敛——不，不应该收敛' if success else '✅ 正确识别不可达'}")
    print(f"最终误差: {errors_far[-1]:.4f}")
    print("→ 面试话术：'VLA 也可能规划出不可达的抓取点，要靠 IK solver 报错来兜底'")


def animate_ik():
    """动画：拖动目标点，机械臂实时 IK 求解"""
    arm = TwoLinkArm()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_title('FK/IK 动画演示：目标沿圆运动，肘朝上/朝下双解', fontsize=12)

    target_line, = ax.plot([], [], 'r*', markersize=15)
    arm_up_line1, = ax.plot([], [], 'b-o', linewidth=3, alpha=0.8, label='肘朝上')
    arm_up_line2, = ax.plot([], [], 'b--o', linewidth=3, alpha=0.8)
    arm_down_line1, = ax.plot([], [], 'g-o', linewidth=2, alpha=0.6, label='肘朝下')
    arm_down_line2, = ax.plot([], [], 'g--o', linewidth=2, alpha=0.6)
    ax.legend(fontsize=10)

    def update(frame):
        # 目标沿圆运动
        theta = frame * 0.05
        tx = 1.2 * np.cos(theta)
        ty = 1.2 * np.sin(theta) + 0.3
        target_line.set_data([tx], [ty])

        # 肘朝上解
        sol_up = arm.ik(tx, ty, elbow_up=True)
        if sol_up and abs(tx**2 + ty**2) < (arm.l1 + arm.l2)**2:
            t1, t2, _, _ = sol_up
            _, _, jx, jy, eex, eey = arm.get_arm_points(t1, t2)
            arm_up_line1.set_data([0, jx], [0, jy])
            arm_up_line2.set_data([jx, eex], [jy, eey])
            arm_up_line1.set_visible(True)
            arm_up_line2.set_visible(True)
        else:
            arm_up_line1.set_visible(False)
            arm_up_line2.set_visible(False)

        # 肘朝下解
        sol_down = arm.ik(tx, ty, elbow_up=False)
        if sol_down and abs(tx**2 + ty**2) < (arm.l1 + arm.l2)**2:
            t1, t2, _, _ = sol_down
            _, _, jx, jy, eex, eey = arm.get_arm_points(t1, t2)
            arm_down_line1.set_data([0, jx], [0, jy])
            arm_down_line2.set_data([jx, eex], [jy, eey])
            arm_down_line1.set_visible(True)
            arm_down_line2.set_visible(True)
        else:
            arm_down_line1.set_visible(False)
            arm_down_line2.set_visible(False)

        return target_line, arm_up_line1, arm_up_line2, arm_down_line1, arm_down_line2

    ani = animation.FuncAnimation(fig, update, frames=200, interval=50, blit=True)
    plt.show()


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("FK/IK 仿真器 —— 面试级可视化演示")
    print("=" * 60)
    print("\n选择演示模式：")
    print("  1 — 2 连杆 FK/IK 双解 + 可达空间图（静态）")
    print("  2 — 5-DOF 数值 IK（终端输出）")
    print("  3 — 动画：目标沿圆运动，双解实时更新")
    print("  0 — 全部运行")

    try:
        choice = int(input("\n请输入 (0/1/2/3): ") or "0")
    except ValueError:
        choice = 0

    if choice in (0, 1):
        demo_two_link_arm()
    if choice in (0, 2):
        demo_numerical_ik()
    if choice in (0, 3):
        animate_ik()

    print("\n✅ FK/IK 仿真完成")
    print("💡 面试话术：'我写过一个 FK/IK 仿真，用 2 连杆演示了'多解'（肘朝上/朝下）、")
    print("   '不可达'（目标超出工作空间）、和'奇异位姿'（自由度降级）。")
    print("   这些概念在 VLA 翻车时就是底层根本原因。'")
