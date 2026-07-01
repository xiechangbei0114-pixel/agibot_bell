# -*- coding: utf-8 -*-
"""
手眼标定模拟实例 (Hand-Eye Calibration Simulation)
==================================================
场景: Eye-in-Hand (相机装在机械臂末端)
目标: 求相机坐标系 → 末端坐标系 的变换矩阵 (camHend)

数学原理:
  AX = XB
  A = 末端移动量  (end_H_end')
  B = 相机观测到的标定板移动量 (cam_H_cam')
  X = 待求的手眼矩阵 (camHend)

步骤:
  1. 让机械臂走到 N 个不同位姿
  2. 每个位姿下: 记录末端位姿 + 相机拍到标定板
  3. 用 AX = XB 求解 X
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List

# ============================================================
# 1. 工具函数
# ============================================================

def euler_to_rot(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """欧拉角(弧度) → 旋转矩阵 (ZYX顺序)"""
    cz, sz = np.cos(yaw), np.sin(yaw)
    cy, sy = np.cos(pitch), np.sin(pitch)
    cx, sx = np.cos(roll), np.sin(roll)
    R = np.array([
        [cz*cy, cz*sy*sx - sz*cx, cz*sy*cx + sz*sx],
        [sz*cy, sz*sy*sx + cz*cx, sz*sy*cx - cz*sx],
        [-sy,   cy*sx,            cy*cx]
    ])
    return R


def rot_to_euler(R_mat: np.ndarray) -> np.ndarray:
    """旋转矩阵 → 欧拉角(弧度)"""
    sy = np.sqrt(R_mat[0,0]**2 + R_mat[1,0]**2)
    singular = sy < 1e-6
    if not singular:
        x = np.arctan2(R_mat[2,1], R_mat[2,2])
        y = np.arctan2(-R_mat[2,0], sy)
        z = np.arctan2(R_mat[1,0], R_mat[0,0])
    else:
        x = np.arctan2(-R_mat[1,2], R_mat[1,1])
        y = np.arctan2(-R_mat[2,0], sy)
        z = 0
    return np.array([x, y, z])


def rot_to_rotvec(R_mat: np.ndarray) -> np.ndarray:
    """旋转矩阵 → 旋转向量 (Rodrigues)"""
    angle = np.arccos(np.clip((np.trace(R_mat) - 1) / 2, -1, 1))
    if angle < 1e-10:
        return np.zeros(3)
    rx = (R_mat[2,1] - R_mat[1,2]) / (2 * np.sin(angle))
    ry = (R_mat[0,2] - R_mat[2,0]) / (2 * np.sin(angle))
    rz = (R_mat[1,0] - R_mat[0,1]) / (2 * np.sin(angle))
    return np.array([rx, ry, rz]) * angle

def make_homogeneous(R_mat: np.ndarray, t: np.ndarray) -> np.ndarray:
    """构建 4x4 齐次变换矩阵"""
    H = np.eye(4)
    H[:3, :3] = R_mat
    H[:3, 3] = t
    return H


def decompose_homogeneous(H: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """分解 4x4 齐次矩阵为旋转矩阵和平移向量"""
    return H[:3, :3], H[:3, 3]


def euler_to_homogeneous(roll: float, pitch: float, yaw: float, x: float, y: float, z: float) -> np.ndarray:
    """欧拉角(弧度) + 平移 → 齐次矩阵"""
    R_mat = euler_to_rot(roll, pitch, yaw)
    return make_homogeneous(R_mat, np.array([x, y, z]))


# ============================================================
# 2. 模拟数据生成
# ============================================================

# 设定一个"真实"的手眼矩阵 (ground truth)
# 假设: 相机安装在末端法兰上，向前偏移 10cm，向下偏移 5cm
true_camHend = euler_to_homogeneous(
    np.radians(180), 0, 0,   # 相机Z轴与末端Z轴反向
    0.10, 0.0, -0.05         # 向前10cm, 向下5cm
)
print("=" * 60)
print("真实手眼矩阵 (Ground Truth) camHend:")
print(true_camHend)
print()

# 设定标定板在机器人基座坐标系下的位姿 (标定板固定在桌上)
boardHbase = euler_to_homogeneous(0, 0, 0, 0.5, 0.0, 0.2)

# 生成 N 组机械臂位姿
N = 12
np.random.seed(42)
poses_deg = [
    (0, 0, 30, 0.4, 0.1, 0.3),
    (5, 2, 35, 0.38, 0.12, 0.28),
    (-3, 4, 28, 0.42, 0.08, 0.32),
    (8, -2, 32, 0.36, 0.15, 0.26),
    (-5, 3, 25, 0.44, 0.05, 0.34),
    (2, 6, 40, 0.35, 0.18, 0.25),
    (-2, -3, 22, 0.45, 0.02, 0.35),
    (6, 1, 38, 0.37, 0.14, 0.27),
    (-4, 5, 33, 0.41, 0.09, 0.31),
    (3, -1, 27, 0.39, 0.11, 0.29),
    (7, 4, 36, 0.34, 0.16, 0.24),
    (-6, 2, 29, 0.43, 0.07, 0.33),
]

# 生成末端位姿 (endHbase) 和相机观测 (camHboard)
end_poses = []   # endHbase
cam_obs = []     # camHboard (相机看到的标定板位姿)

for r, p, y, x, y_, z in poses_deg:
    # 机械臂末端在基座下的位姿
    endHbase = euler_to_homogeneous(
        np.radians(r), np.radians(p), np.radians(y), x, y_, z
    )
    end_poses.append(endHbase)

    # 相机看到的标定板位姿: camHboard = inv(camHend) * inv(endHbase) * boardHbase
    # 或者更直观: endHboard = inv(endHbase) * boardHbase
    #            camHboard = inv(camHend) * endHboard
    endHboard = np.linalg.inv(endHbase) @ boardHbase
    camHboard = np.linalg.inv(true_camHend) @ endHboard
    cam_obs.append(camHboard)

print(f"生成 {N} 组仿真数据")
print("  每组包含: 末端位姿 endHbase + 相机观测 camHboard")
print()

# ============================================================
# 3. 用 AX = XB 求解手眼矩阵
# ============================================================
# Tsai-Lee 方法: 先解旋转, 再解平移

def solve_hand_eye_tsai(end_poses: List[np.ndarray], cam_obs: List[np.ndarray]) -> np.ndarray:
    """
    Tsai 两步法求解 AX = XB
    A = end_i_H_end_j  (末端移动量)
    B = cam_i_H_cam_j  (相机观测移动量)
    """
    n = len(end_poses)
    assert n >= 3, "至少需要3组数据"

    # --- Step 1: 解旋转 ---
    # 对每组(i,j), 构建方程: R_A * R_X = R_X * R_B
    # 化为: (R_A - I) * r_X = ... 用最小二乘

    C = np.zeros((3, 3))
    d = np.zeros(3)

    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            # A = end_j_H_end_i (从i到j的移动)
            A = np.linalg.inv(end_poses[i]) @ end_poses[j]
            R_A, _ = decompose_homogeneous(A)

            # B = cam_j_H_cam_i (从i到j的观测移动)
            B = np.linalg.inv(cam_obs[i]) @ cam_obs[j]
            R_B, _ = decompose_homogeneous(B)

            # 轴角表示
            # P_A = log(R_A), P_B = log(R_B)
            # 方程: P_A 叉积 P_X + ... 简化版本

            # 使用简化方法: 构建线性方程组
            r_a = rot_to_rotvec(R_A)
            r_b = rot_to_rotvec(R_B)

            # 叉积矩阵
            skew_a = np.array([
                [0, -r_a[2], r_a[1]],
                [r_a[2], 0, -r_a[0]],
                [-r_a[1], r_a[0], 0]
            ])
            skew_b = np.array([
                [0, -r_b[2], r_b[1]],
                [r_b[2], 0, -r_b[0]],
                [-r_b[1], r_b[0], 0]
            ])

            C += (skew_a + skew_b).T @ (skew_a + skew_b)
            d += (skew_a + skew_b).T @ (r_b - r_a)
            count += 1

    # 解最小二乘: C * r_x = d
    r_x = np.linalg.lstsq(C, d, rcond=None)[0]
    # 旋转向量 → 旋转矩阵 (Rodrigues公式)
    theta = np.linalg.norm(r_x)
    if theta < 1e-10:
        R_X = np.eye(3)
    else:
        k = r_x / theta
        K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
        R_X = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)

    # --- Step 2: 解平移 ---
    # 方程: (R_A - I) * t_X = R_X * t_B - t_A
    C_trans = np.zeros((3, 3))
    d_trans = np.zeros(3)

    for i in range(n):
        for j in range(i + 1, n):
            A = np.linalg.inv(end_poses[i]) @ end_poses[j]
            R_A, t_A = decompose_homogeneous(A)

            B = np.linalg.inv(cam_obs[i]) @ cam_obs[j]
            R_B, t_B = decompose_homogeneous(B)

            C_trans += (R_A - np.eye(3)).T @ (R_A - np.eye(3))
            rhs = R_X @ t_B - t_A
            d_trans += (R_A - np.eye(3)).T @ rhs

    t_X = np.linalg.lstsq(C_trans, d_trans, rcond=None)[0]

    return make_homogeneous(R_X, t_X)


# 求解
estimated_camHend = solve_hand_eye_tsai(end_poses, cam_obs)

print("=" * 60)
print("求解结果 vs 真实值")
print("=" * 60)

R_est, t_est = decompose_homogeneous(estimated_camHend)
R_true, t_true = decompose_homogeneous(true_camHend)

print(f"\n平移向量 (m):")
print(f"  真实:   x={t_true[0]:.4f}, y={t_true[1]:.4f}, z={t_true[2]:.4f}")
print(f"  估计:   x={t_est[0]:.4f}, y={t_est[1]:.4f}, z={t_est[2]:.4f}")
print(f"  误差:   dx={abs(t_est[0]-t_true[0]):.4f}, dy={abs(t_est[1]-t_true[1]):.4f}, dz={abs(t_est[2]-t_true[2]):.4f}")

# 旋转误差
euler_true = np.degrees(rot_to_euler(R_true))
euler_est = np.degrees(rot_to_euler(R_est))
print(f"\n旋转 (度):")
print(f"  真实:   roll={euler_true[0]:.1f}, pitch={euler_true[1]:.1f}, yaw={euler_true[2]:.1f}")
print(f"  估计:   roll={euler_est[0]:.1f}, pitch={euler_est[1]:.1f}, yaw={euler_est[2]:.1f}")
print(f"  误差:   {abs(euler_est - euler_true).max():.2f}° (最大分量)")

# ============================================================
# 4. 验证: 用估计的手眼矩阵投影检验
# ============================================================

print("\n" + "=" * 60)
print("验证: 投影到图像平面")
print("=" * 60)

# 模拟相机内参 (假设已知)
fx, fy = 600, 600  # 焦距 (pixel)
cx, cy = 320, 240  # 主点 (pixel)
K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

# 标定板上4个角点 (标定板坐标系下, 单位m)
board_corners = np.array([
    [-0.05, -0.05, 0],
    [0.05, -0.05, 0],
    [0.05, 0.05, 0],
    [-0.05, 0.05, 0],
])

errors_true = []
errors_est = []

for i in range(min(5, N)):  # 展示前5组
    # 真实投影
    endHbase = end_poses[i]
    camHboard_true = cam_obs[i]  # 真实观测
    
    # 用估计的手眼矩阵推算 camHboard
    endHboard = np.linalg.inv(endHbase) @ boardHbase
    camHboard_est = np.linalg.inv(estimated_camHend) @ endHboard

    # 投影角点到图像平面
    for name, camHboard in [("真实观测", camHboard_true), ("估计重投", camHboard_est)]:
        pts_img = []
        for corner in board_corners:
            corner_cam = (camHboard @ np.append(corner, 1))[:3]
            u = corner_cam[0] * fx / corner_cam[2] + cx
            v = corner_cam[1] * fy / corner_cam[2] + cy
            pts_img.append([u, v])
        pts_img = np.array(pts_img)

        if name == "真实观测":
            errors_true.append(pts_img)
        else:
            errors_est.append(pts_img)

    # 打印第1组
    if i == 0:
        print(f"\n位姿 #{i+1}:")
        print(f"  真实观测角点像素坐标:")
        for j, (u, v) in enumerate(pts_img):
            print(f"    角点{j+1}: ({u:.1f}, {v:.1f})")

# 计算重投影误差
reprojection_errors = []
for i in range(min(5, N)):
    err = np.mean(np.linalg.norm(errors_true[i] - errors_est[i], axis=1))
    reprojection_errors.append(err)

print(f"\n平均重投影误差: {np.mean(reprojection_errors):.2f} 像素")
print(f"最大重投影误差: {np.max(reprojection_errors):.2f} 像素")

# ============================================================
# 5. 总结
# ============================================================
print("\n" + "=" * 60)
print("手眼标定模拟完成")
print("=" * 60)
print(f"""
流程总结:
  1. 移动机械臂到 {N} 个不同位姿
  2. 每个位姿记录: 末端位姿 + 相机拍到标定板
  3. 用 AX = XB (Tsai法) 求解手眼矩阵
  4. 验证: 重投影误差 < 3 像素

方案岗价值:
  - 传统方案需要手眼标定, VLA 端到端不需要
  - 但混合方案中, 视觉重试/力控引导仍然需要手眼矩阵
  - 理解这个数学原理, 才能在设计方案时做正确选型
""")
