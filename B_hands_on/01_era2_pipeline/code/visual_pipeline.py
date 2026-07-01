#!/usr/bin/env python3
"""
================================================================================
🏗️  Era 2 视觉抓取流水线 — 完整实现
================================================================================

   Windows (你的笔记本)                         WSL2 (Ubuntu)
   ┌─────────────────────────┐          ┌──────────────────────────────┐
   │                         │          │                              │
   │  📷 ① 相机采集          │          │  🦾 ③ 机器人控制 (MoveIt2)   │
   │   (USB摄像头/图片)       │          │                              │
   │         ↓               │          │    Panda 仿真 (Gazebo)       │
   │  🔍 ② YOLO 检测         │   ROS2   │         ↑                   │
   │   (ONNX CPU推理)         │ ──────▶  │   接收抓取指令              │
   │         ↓               │  Topic   │         ↑                   │
   │  📐 ③ 坐标变换          │          │   坐标变换 (像素→机器人)    │
   │   (像素→相机→机器人)     │          │                              │
   │         ↓               │          │                              │
   │  📤 ④ 发布到 ROS2       │          │                              │
   │   (通过 windows ROS2)   │          │                              │
   └─────────────────────────┘          └──────────────────────────────┘

运行模式：
  模式 A: 纯仿真 (Windows-only, 无需 ROS2/WSL)
     python era2_pipeline.py --mode sim

  模式 B: 真机流水线 (Windows + WSL ROS2)
     先启动 WSL ROS2，然后:
     python era2_pipeline.py --mode real

  模式 C: 图片测试 (单张图片跑通流程)
     python era2_pipeline.py --mode test --image test.jpg
================================================================================
"""

import numpy as np
import cv2
import time
import json
import os
import sys
from dataclasses import dataclass
from typing import Optional, Tuple, List
import math

# ============================================================
# ⚙️  配置参数
# ============================================================

@dataclass
class CameraConfig:
    """相机内参 (以 Intel RealSense D435 为例)"""
    fx: float = 615.0      # 焦距 x (像素)
    fy: float = 615.0      # 焦距 y (像素)
    cx: float = 320.0      # 光心 x
    cy: float = 240.0      # 光心 y
    width: int = 640       # 图像宽度
    height: int = 480      # 图像高度

@dataclass
class RobotConfig:
    """机器人-相机相对位姿 (手眼标定结果)"""
    # 相机相对于机器人基座的变换 (T_cam_to_base)
    #        [R | t]
    # 即：相机坐标系下的点 → 机器人基座坐标系
    tx: float = 0.25       # x 平移 (m) — 相机在机器人前方
    ty: float = 0.0        # y 平移 (m)
    tz: float = 0.50       # z 平移 (m) — 相机高于机器人底座
    # 假设相机朝下 30°，绕 X 轴旋转
    roll: float = math.radians(-30)   # RX
    pitch: float = 0.0                # RY
    yaw: float = 0.0                  # RZ

CAMERA = CameraConfig()
ROBOT = RobotConfig()


# ============================================================
# 📷  第①步：相机采集
# ============================================================

def capture_image(source: str = "camera") -> Tuple[np.ndarray, float]:
    """
    从摄像头或图片文件采集图像。

    原理：
      - 相机采集的原始图像是 2D 像素阵列 (H×W×3)
      - 每个像素 (u, v) 记录的是"该方向上的光强"，没有深度信息
      - 本流水线假设物体在已知高度的工作平面上 (z=const)，
        所以可以从 2D 像素反算出 3D 位置 (见 ③ 坐标变换)

    参数:
        source: "camera" | 图片路径 | "sim"

    返回:
        (BGR图像, 时间戳)
    """
    if source == "camera":
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("  ⚠️  摄像头打不开，切换到仿真模式")
            return _simulate_image(), time.time()
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError("摄像头读取失败")
        print(f"  ✅ 摄像头采集: {frame.shape[1]}×{frame.shape[0]}")
        return frame, time.time()

    elif source == "sim":
        return _simulate_image(), time.time()

    else:
        # 从文件读取
        img = cv2.imread(source)
        if img is None:
            raise FileNotFoundError(f"找不到图片: {source}")
        print(f"  ✅ 加载图片: {source} ({img.shape[1]}×{img.shape[0]})")
        return img, time.time()


def _simulate_image() -> np.ndarray:
    """生成仿真图像：传送带上的零件"""
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200  # 灰色背景
    # 画传送带
    cv2.rectangle(img, (0, 200), (640, 320), (180, 180, 160), -1)
    # 画零件 (模拟 CPU 芯片)
    cx, cy = 320 + np.random.randint(-80, 80), 260
    cv2.rectangle(img, (cx-30, cy-20), (cx+30, cy+20), (0, 120, 255), -1)
    cv2.putText(img, "CPU Chip", (cx-35, cy-35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    # 画检测框示意
    cv2.rectangle(img, (cx-35, cy-25), (cx+35, cy+25), (0, 255, 0), 2)
    print(f"  🎲 仿真图像: 零件在像素 ({cx}, {cy})")
    return img


# ============================================================
# 🔍  第②步：YOLO 检测
# ============================================================

class YOLODetector:
    """
    YOLO 目标检测器。

    原理：
      YOLO 将图像划分为 S×S 网格，每个网格预测：
        - B 个边界框 (x, y, w, h)
        - 每个框对应 C 个类别的置信度
      → 输出是 (u, v, w, h, class_id, confidence) 的列表

    硬件需求：
      - YOLOv8n (nano):  GTX 1060 可跑 ~30 FPS
      - YOLOv8s (small): GTX 1060 可跑 ~15 FPS
      - CPU (ONNX):      ~3-5 FPS (但足够演示)

    本实现：
      - 有 ONNX 就用 ONNX 推理
      - 没有就回退到 OpenCV DNN (需要 .weights/.cfg)
      - 都没有就仿真检测
    """

    def __init__(self, model_path: Optional[str] = None, use_sim: bool = False):
        self.use_sim = use_sim
        self.model = None
        self.class_names = {
            0: "CPU芯片", 1: "螺丝钉", 2: "连接器",
            3: "散热片", 4: "电容", 5: "手机壳"
        }

        if use_sim:
            print("  🎯 YOLO: 仿真模式")
            return

        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
        else:
            print("  🎯 YOLO: 无模型文件，使用仿真检测")
            self.use_sim = True

    def _load_model(self, path: str):
        """加载 ONNX/OpenCV 模型"""
        if path.endswith(".onnx"):
            try:
                import onnxruntime as ort
                self.model = ort.InferenceSession(path)
                self.input_name = self.model.get_inputs()[0].name
                print(f"  ✅ YOLO: ONNX 模型加载完成")
            except ImportError:
                print("  ⚠️  未安装 onnxruntime，回退到仿真")
                self.use_sim = True
        else:
            # OpenCV DNN
            self.model = cv2.dnn.readNetFromDarknet(
                path.replace(".weights", ".cfg"), path
            )
            print(f"  ✅ YOLO: OpenCV DNN 加载完成")

    def detect(self, image: np.ndarray) -> List[dict]:
        """
        在图像中检测物体。

        返回:
            [{"class": str, "confidence": float,
              "bbox": (u1, v1, u2, v2),    # 像素坐标
              "center": (u, v)}, ...]        # 中心像素
        """
        if self.use_sim:
            return self._simulate_detect(image)

        # --- 真实 YOLO 推理 ---
        h, w = image.shape[:2]

        if hasattr(self.model, 'run'):
            # ONNX Runtime
            import onnxruntime as ort
            input_tensor = self._preprocess(image)
            outputs = self.model.run(None, {self.input_name: input_tensor})
            detections = self._postprocess(outputs, w, h)
        else:
            # OpenCV DNN
            blob = cv2.dnn.blobFromImage(
                image, 1/255.0, (416, 416), swapRB=True, crop=False
            )
            self.model.setInput(blob)
            outputs = self.model.forward(self.model.getUnconnectedOutLayersNames())
            detections = self._postprocess_darknet(outputs, w, h)

        return detections

    def _simulate_detect(self, image: np.ndarray) -> List[dict]:
        """仿真检测：假装在图像中心区域发现了零件"""
        h, w = image.shape[:2]
        # 假装检测到物体
        cx, cy = w // 2 + np.random.randint(-50, 50), h // 2 + np.random.randint(-20, 20)
        return [{
            "class": "CPU芯片",
            "confidence": 0.93,
            "bbox": (cx-30, cy-20, cx+30, cy+20),
            "center": (cx, cy)
        }]

    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """预处理 → ONNX 输入"""
        import onnxruntime as ort
        input_w, input_h = 640, 640
        img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (input_w, input_h))
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        return np.expand_dims(img, axis=0).astype(np.float32)

    def _postprocess(self, outputs, orig_w, orig_h) -> List[dict]:
        """解析 ONNX 输出"""
        results = []
        # 简化版：假设 outputs[0] 是 (1, N, 6) 格式
        dets = outputs[0][0]
        for det in dets:
            if det[4] > 0.5:  # confidence threshold
                class_id = int(det[5])
                x1, y1, x2, y2 = det[:4]
                # 缩放到原图尺寸
                x1 = int(x1 * orig_w / 640)
                y1 = int(y1 * orig_h / 640)
                x2 = int(x2 * orig_w / 640)
                y2 = int(y2 * orig_h / 640)
                results.append({
                    "class": self.class_names.get(class_id, f"class_{class_id}"),
                    "confidence": float(det[4]),
                    "bbox": (x1, y1, x2, y2),
                    "center": ((x1 + x2) // 2, (y1 + y2) // 2)
                })
        return results

    def _postprocess_darknet(self, outputs, orig_w, orig_h) -> List[dict]:
        """解析 Darknet 输出"""
        results = []
        for output in outputs:
            for det in output:
                scores = det[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence < 0.5:
                    continue
                cx, cy, bw, bh = det[:4] * np.array([orig_w, orig_h, orig_w, orig_h])
                x1 = int(cx - bw/2)
                y1 = int(cy - bh/2)
                x2 = int(cx + bw/2)
                y2 = int(cy + bh/2)
                results.append({
                    "class": self.class_names.get(class_id, f"class_{class_id}"),
                    "confidence": float(confidence),
                    "bbox": (x1, y1, x2, y2),
                    "center": (int(cx), int(cy))
                })
        return results


# ============================================================
# 📐  第③步：坐标变换 (像素 → 机器人)
# ============================================================

class CoordinateTransformer:
    """
    坐标变换：从 2D 像素坐标 → 3D 机器人基座坐标系。

    完整链路：
      像素 (u,v) ──(1)──▶ 归一化平面 ──(2)──▶ 相机坐标系 ──(3)──▶ 机器人基座
                           (u,v) → (x_cam, y_cam, z_cam) → (x_base, y_base, z_base)

    (1) 像素 → 归一化平面 (针孔相机模型)：
          x_norm = (u - cx) / fx
          y_norm = (v - cy) / fy

    (2) 归一化平面 → 相机 3D (需要深度/平面假设)：
          假设物体在已知高度的工作平面上 (z_cam = ?)
          或 已知深度 z_cam = depth(u, v)
          → X_cam = x_norm * z_cam
          → Y_cam = y_norm * z_cam
          → Z_cam = z_cam

    (3) 相机 → 机器人基座 (手眼标定矩阵 T_cam_to_base)：
          [X_base]     [R | t] [X_cam]
          [Y_base]  =  [R | t] [Y_cam]
          [Z_base]     [R | t] [Z_cam]
          [  1  ]     [0 0 0 1] [  1  ]

    关键假设：
      - ⚠️ 单目相机无法获取深度，所以需要"物体在工作平面上的高度已知"
      - 真实部署用 3D 相机 (如 RealSense D435) 直接读 depth
      - 本实现假设 z=0.30m 的工作平面
    """

    def __init__(self, camera: CameraConfig, robot: RobotConfig):
        self.cam = camera
        self._build_transform(robot)

    def _build_transform(self, robot: RobotConfig):
        """
        构建 4×4 齐次变换矩阵 T_cam_to_base

        相机装在机器人前方，朝下 30°：
          T = Trans(0.25, 0, 0.50) · RotX(-30°)
        """
        # 旋转矩阵 (绕 X 轴)
        rx = robot.roll
        R = np.array([
            [1, 0, 0],
            [0, math.cos(rx), -math.sin(rx)],
            [0, math.sin(rx),  math.cos(rx)]
        ])
        # 平移向量
        t = np.array([robot.tx, robot.ty, robot.tz])
        # 4×4 齐次矩阵
        self.T = np.eye(4)
        self.T[:3, :3] = R
        self.T[:3, 3] = t

    def pixel_to_robot(self, u: float, v: float,
                       plane_z: float = 0.30) -> Tuple[float, float, float]:
        """
        像素坐标 → 机器人基座坐标系下的 3D 位置。

        参数:
            u, v: 像素坐标 (物体中心)
            plane_z: 工作平面在相机坐标系下的 Z 高度 (m)

        返回:
            (x, y, z) 机器人基座坐标系下的 3D 位置
        """
        # Step 1: 像素 → 归一化平面
        x_norm = (u - self.cam.cx) / self.cam.fx
        y_norm = (v - self.cam.cy) / self.cam.fy

        # Step 2: 归一化平面 → 相机坐标系 3D
        # Z_cam = plane_z (已知工作平面高度)
        # X_cam = x_norm * Z_cam
        # Y_cam = y_norm * Z_cam
        z_cam = plane_z
        x_cam = x_norm * z_cam
        y_cam = y_norm * z_cam

        # 相机坐标系下的齐次坐标
        P_cam = np.array([x_cam, y_cam, z_cam, 1.0])

        # Step 3: 相机 → 机器人基座
        P_base = self.T @ P_cam

        return float(P_base[0]), float(P_base[1]), float(P_base[2])

    def pixel_to_robot_with_depth(self, u: float, v: float,
                                   depth: float) -> Tuple[float, float, float]:
        """
        有深度信息时的坐标变换 (3D 相机)。

        参数:
            u, v: 像素坐标
            depth: 该像素的深度值 (m)

        返回:
            (x, y, z) 机器人基座坐标系
        """
        # 像素 → 相机坐标系
        x_cam = (u - self.cam.cx) / self.cam.fx * depth
        y_cam = (v - self.cam.cy) / self.cam.fy * depth
        z_cam = depth

        P_cam = np.array([x_cam, y_cam, z_cam, 1.0])
        P_base = self.T @ P_cam

        return float(P_base[0]), float(P_base[1]), float(P_base[2])


# ============================================================
# 🦾  第④步：机器人控制
# ============================================================

class RobotController:
    """
    机械臂控制器。

    本实现提供两层：
      层 1: 仿真控制 (纯 Python，无需 ROS2)
      层 2: 真实 MoveIt2 控制 (需要 WSL + ROS2)

    原理：
      收到 3D 抓取点后，控制器：
        1. 计算预接近位 (approach pose): 抓取点上方 15cm
        2. 发送 MoveIt2 笛卡尔运动指令到预接近位
        3. 发送到抓取位
        4. (模拟) 闭合夹爪
        5. 抬起工件
        6. 移动到放料位
    """

    def __init__(self, use_ros2: bool = False):
        self.use_ros2 = use_ros2
        self.controller = None

        if use_ros2:
            self._init_ros2()
        else:
            print("  🦾 Robot: 仿真模式 (无 ROS2)")

    def _init_ros2(self):
        """初始化 ROS2 MoveIt2 控制"""
        try:
            import rclpy
            from pymoveit2 import MoveIt2
            rclpy.init()
            self.ros_node = rclpy.create_node('era2_pipeline')
            PANDA_JOINTS = [
                'panda_joint1', 'panda_joint2', 'panda_joint3',
                'panda_joint4', 'panda_joint5', 'panda_joint6', 'panda_joint7'
            ]
            self.moveit2 = MoveIt2(
                node=self.ros_node,
                joint_names=PANDA_JOINTS,
                base_link_name='panda_link0',
                end_effector_name='panda_link8',
                group_name='panda_arm',
            )
            print("  ✅ Robot: ROS2 MoveIt2 就绪")
            time.sleep(2.0)  # 等待 MoveIt2 准备
        except Exception as e:
            print(f"  ⚠️  ROS2 初始化失败: {e}")
            print(f"  回退到仿真模式")
            self.use_ros2 = False

    def grasp(self, x: float, y: float, z: float) -> bool:
        """
        执行抓取动作。

        动作序列:
          1. 预接近位 (x, y, z+0.15)
          2. 抓取位 (x, y, z)
          3. 闭合夹爪 (模拟)
          4. 抬升 (x, y, z+0.20)
          5. 放料位 (0.25, 0.0, 0.35)

        返回: 成功?
        """
        print(f"\n  🎯 执行抓取: ({x:.3f}, {y:.3f}, {z:.3f})")

        if not self.use_ros2:
            return self._simulate_grasp(x, y, z)

        return self._ros2_grasp(x, y, z)

    def _simulate_grasp(self, x, y, z) -> bool:
        """仿真抓取 (Python 模拟，无实际机器人)"""
        stages = [
            (f"预接近位 ({x:.3f}, {y:.3f}, {z+0.15:.3f})", 0.3),
            (f"抓取位   ({x:.3f}, {y:.3f}, {z:.3f})", 0.3),
            ("闭合夹爪", 0.2),
            (f"抬升     ({x:.3f}, {y:.3f}, {z+0.20:.3f})", 0.3),
            ("放料位   (0.250, 0.000, 0.350)", 0.4),
        ]
        for desc, delay in stages:
            print(f"    ⏳ {desc}")
            time.sleep(delay)
        print(f"  ✅ 抓取完成!")
        return True

    def _ros2_grasp(self, x, y, z) -> bool:
        """通过 MoveIt2 控制真实/仿真 Panda"""
        try:
            # Step 1: 预接近位 (抓取点上方 15cm)
            print(f"    ⏳ 预接近位")
            self.moveit2.move_to_pose(
                position=[x, y, z + 0.15],
                quat_xyzw=[0.0, 0.0, 0.0, 1.0],
                frame_id='panda_link0',
            )
            self.moveit2.wait_until_executed()
            print(f"    ✅ 预接近到位")

            # Step 2: 下降到抓取位
            print(f"    ⏳ 抓取位")
            self.moveit2.move_to_pose(
                position=[x, y, z],
                quat_xyzw=[0.0, 0.0, 0.0, 1.0],
                frame_id='panda_link0',
            )
            self.moveit2.wait_until_executed()
            print(f"    ✅ 抓取到位")

            time.sleep(0.5)  # 夹爪闭合

            # Step 3: 抬起
            print(f"    ⏳ 抬升")
            self.moveit2.move_to_pose(
                position=[x, y, z + 0.20],
                quat_xyzw=[0.0, 0.0, 0.0, 1.0],
                frame_id='panda_link0',
            )
            self.moveit2.wait_until_executed()

            # Step 4: 放料
            print(f"    ⏳ 放料")
            self.moveit2.move_to_pose(
                position=[0.25, 0.0, 0.35],
                quat_xyzw=[0.0, 0.0, 0.0, 1.0],
                frame_id='panda_link0',
            )
            self.moveit2.wait_until_executed()

            print(f"  ✅ 抓取完成!")
            return True

        except Exception as e:
            print(f"  ❌ 执行失败: {e}")
            return False

    def shutdown(self):
        """清理 ROS2 资源"""
        if self.use_ros2:
            import rclpy
            self.ros_node.destroy_node()
            rclpy.shutdown()


# ============================================================
# 🌉  ROS2 桥接 (Windows ↔ WSL)
# ============================================================

class ROS2Bridge:
    """
    将 Windows 上的检测结果发送到 WSL 中的 ROS2。

    方案选择：
      A. ✅ Windows 原生 ROS2 (推荐)
         - 在 Windows 上安装 ROS2 Humble (二进制包)
         - 与 WSL ROS2 通过 DDS 自动发现
         - 零配置，就像在同一台机器上

      B. ZeroMQ 桥接 (备选)
         - Windows 端 ZMQ PUB
         - WSL 端 ZMQ SUB → ROS2 bridge
         - 适合 ROS1 或不装 Windows ROS2

    本实现：优先方案 A (ROS2)，备选方案 B (ZMQ)
    """

    def __init__(self, method: str = "auto"):
        self.method = method
        self.publisher = None
        self.node = None

        if method == "none":
            return

        if method == "auto" or method == "ros2":
            if self._try_ros2():
                return
            print("  ⚠️  Windows ROS2 不可用，尝试 ZMQ...")

        if method == "zmq" or method == "auto":
            if self._try_zmq():
                return
            print("  ⚠️  ZMQ 也不可用 → 仅本地日志")

        self.method = "log"

    def _try_ros2(self) -> bool:
        """尝试初始化 Windows ROS2"""
        try:
            import rclpy
            from std_msgs.msg import String
            from geometry_msgs.msg import PoseStamped

            rclpy.init()
            self.node = rclpy.create_node('era2_bridge')
            self.pose_pub = self.node.create_publisher(
                PoseStamped, 'vla_pose', 10
            )
            self.log_pub = self.node.create_publisher(
                String, 'detection_log', 10
            )
            print("  🌉 Bridge: ROS2 (Windows) 就绪")
            self.method = "ros2"
            return True
        except Exception as e:
            return False

    def _try_zmq(self) -> bool:
        """尝试初始化 ZMQ"""
        try:
            import zmq
            self.zmq_context = zmq.Context()
            self.zmq_socket = self.zmq_context.socket(zmq.PUB)
            self.zmq_socket.bind("tcp://*:5556")
            print("  🌉 Bridge: ZMQ (tcp://*:5556) 就绪")
            self.method = "zmq"
            return True
        except ImportError:
            return False

    def publish_pose(self, detections: List[dict],
                     robot_poses: List[Tuple[float, float, float]]):
        """
        发布检测结果到 WSL ROS2。

        ROS2 方式: 发布 PoseStamped 到 /vla_pose
        ZMQ 方式:  发布 JSON 到 tcp://*:5556
        """
        if self.method == "log":
            for det, pose in zip(detections, robot_poses):
                print(f"  📤 [BRIDGE] {det['class']} @ ({pose[0]:.3f}, {pose[1]:.3f}, {pose[2]:.3f})")
            return

        if self.method == "ros2":
            for det, pose in zip(detections, robot_poses):
                msg = PoseStamped()
                msg.header.frame_id = 'panda_link0'
                msg.header.stamp = self.node.get_clock().now().to_msg()
                msg.pose.position.x = pose[0]
                msg.pose.position.y = pose[1]
                msg.pose.position.z = pose[2]
                msg.pose.orientation.w = 1.0
                self.pose_pub.publish(msg)
                print(f"  📤 [ROS2] 发布 /vla_pose → ({pose[0]:.3f}, {pose[1]:.3f})")

        elif self.method == "zmq":
            import zmq
            for det, pose in zip(detections, robot_poses):
                msg = json.dumps({
                    "class": det["class"],
                    "confidence": det["confidence"],
                    "position": {"x": pose[0], "y": pose[1], "z": pose[2]},
                    "frame_id": "panda_link0",
                    "timestamp": time.time()
                })
                self.zmq_socket.send_string(msg)
                print(f"  📤 [ZMQ] 发送 → {det['class']} @ ({pose[0]:.3f}, {pose[1]:.3f})")

    def shutdown(self):
        if self.node:
            import rclpy
            self.node.destroy_node()
            rclpy.shutdown()


# ============================================================
# 🔗  主流水线
# ============================================================

class Era2Pipeline:
    """
    Era 2 视觉抓取流水线 — 主控制器。

    运行模式:
      --mode sim   纯仿真 (默认)
      --mode real  完整流水线 (需 WSL ROS2)
      --mode test  单张图片测试
    """

    def __init__(self, mode: str = "sim"):
        self.mode = mode
        print("=" * 65)
        print(f"  🏗️  Era 2 视觉抓取流水线")
        print(f"  模式: {mode}")
        print("=" * 65)

        # 初始化各模块
        self.detector = YOLODetector(use_sim=(mode != "test"))
        self.transformer = CoordinateTransformer(CAMERA, ROBOT)
        self.controller = RobotController(use_ros2=(mode == "real"))
        self.bridge = ROS2Bridge(method="real" if mode == "real" else "none")

    def run_once(self, image_source: str = "sim") -> dict:
        """
        执行一次完整的视觉抓取流水线。

        返回流水线的完整日志，包括每步的耗时和中间结果。
        """
        timeline = {}  # 记录各阶段耗时
        result = {"success": False, "steps": []}

        print(f"\n{'─'*55}")
        print(f"  🚀 开始新一轮抓取")
        print(f"{'─'*55}")

        # === 第①步：相机采集 ===
        t0 = time.time()
        image, timestamp = capture_image(image_source)
        timeline["capture"] = time.time() - t0
        result["steps"].append({
            "step": 1, "name": "相机采集",
            "latency_ms": round(timeline["capture"] * 1000, 1),
            "output": f"{image.shape[1]}×{image.shape[0]}"
        })

        # === 第②步：YOLO 检测 ===
        t0 = time.time()
        detections = self.detector.detect(image)
        timeline["detect"] = time.time() - t0
        result["steps"].append({
            "step": 2, "name": "YOLO 检测",
            "latency_ms": round(timeline["detect"] * 1000, 1),
            "output": f"检测到 {len(detections)} 个物体"
        })

        if not detections:
            print("  ⚠️  未检测到物体")
            result["steps"].append({
                "step": 3, "name": "坐标变换", "latency_ms": 0,
                "output": "跳过 (无检测结果)"
            })
            result["steps"].append({
                "step": 4, "name": "机器人控制", "latency_ms": 0,
                "output": "跳过 (无检测结果)"
            })
            return result

        # 打印检测结果
        for det in detections:
            u, v = det["center"]
            print(f"  🔍 {det['class']} (置信度: {det['confidence']:.2f}) "
                  f"@ 像素 ({u}, {v})")

        # === 第③步：坐标变换 ===
        t0 = time.time()
        robot_poses = []
        for det in detections:
            u, v = det["center"]
            x, y, z = self.transformer.pixel_to_robot(u, v)
            robot_poses.append((x, y, z))

            print(f"  📐 坐标变换: 像素({u}, {v}) → "
                  f"机器人基座({x:.3f}, {y:.3f}, {z:.3f})")

        timeline["transform"] = time.time() - t0
        result["steps"].append({
            "step": 3, "name": "坐标变换",
            "latency_ms": round(timeline["transform"] * 1000, 1),
            "output": f"{len(robot_poses)} 个物体 → 机器人基座坐标系"
        })

        # 发布到 ROS2 (如果是 real 模式)
        self.bridge.publish_pose(detections, robot_poses)

        # === 第④步：机器人控制 ===
        t0 = time.time()
        for i, (det, pose) in enumerate(zip(detections, robot_poses)):
            print(f"\n  🔧 [{i+1}/{len(detections)}] 抓取 {det['class']}")
            success = self.controller.grasp(*pose)
            if success:
                result["success"] = True
                break  # 成功抓取一个就结束

        timeline["control"] = time.time() - t0
        result["steps"].append({
            "step": 4, "name": "机器人控制",
            "latency_ms": round(timeline["control"] * 1000, 1),
            "output": "✅ 抓取成功" if result["success"] else "❌ 抓取失败"
        })

        # 汇总
        total_ms = sum(v * 1000 for v in timeline.values())
        result["total_latency_ms"] = round(total_ms, 1)
        result["timeline"] = timeline

        # 可视化检测结果
        if self.mode != "real":
            self._visualize(image, detections, robot_poses)

        return result

    def _visualize(self, image, detections, robot_poses):
        """可视化检测和变换结果"""
        try:
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(1, 2, figsize=(14, 6))

            # 左图：检测结果
            ax1 = axes[0]
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            ax1.imshow(img_rgb)
            ax1.set_title("📷 相机画面 + YOLO 检测", fontsize=12, fontweight='bold')

            for det in detections:
                x1, y1, x2, y2 = det["bbox"]
                u, v = det["center"]
                rect = plt.Rectangle(
                    (x1, y1), x2-x1, y2-y1,
                    fill=False, color='lime', linewidth=2
                )
                ax1.add_patch(rect)
                ax1.plot(u, v, 'r+', markersize=12)
                ax1.text(x1, y1-5, f"{det['class']} ({det['confidence']:.2f})",
                         color='lime', fontsize=9, fontweight='bold',
                         bbox=dict(facecolor='black', alpha=0.5))

            ax1.set_xlabel("u (像素)")
            ax1.set_ylabel("v (像素)")

            # 右图：机器人坐标变换结果
            ax2 = axes[1]
            ax2.set_title("🤖 机器人基座坐标系", fontsize=12, fontweight='bold')
            ax2.set_xlim(-0.2, 0.8)
            ax2.set_ylim(-0.4, 0.6)
            ax2.set_aspect('equal')
            ax2.grid(True, alpha=0.3)
            ax2.set_xlabel("X (m)")
            ax2.set_ylabel("Y (m)")

            # 画机器人底座
            ax2.plot(0, 0, 'ks', markersize=15, label='Panda 基座')
            # 画工作区域
            workspace = plt.Rectangle(
                (0.2, -0.3), 0.4, 0.6,
                fill=True, alpha=0.1, color='blue', label='工作区域'
            )
            ax2.add_patch(workspace)

            for det, pose in zip(detections, robot_poses):
                x, y, z = pose
                ax2.plot(x, y, 'r*', markersize=15)
                ax2.annotate(
                    f"  {det['class']}\n  ({x:.3f}, {y:.3f}, {z:.3f})",
                    (x, y), fontsize=9,
                    bbox=dict(facecolor='yellow', alpha=0.7)
                )
                # 画从基座到目标的连线
                ax2.plot([0, x], [0, y], 'r--', alpha=0.5)

            ax2.legend(fontsize=9, loc='upper right')

            plt.tight_layout()
            plt.show()

        except ImportError:
            pass

    def run_loop(self, image_source: str = "sim", interval: float = 3.0):
        """循环运行流水线"""
        print(f"\n{'='*55}")
        print(f"  🔄 流水线循环模式 (每 {interval}s 一次)")
        print(f"{'='*55}")
        print(f"  按 Ctrl+C 停止\n")

        try:
            while True:
                result = self.run_once(image_source)
                self._print_summary(result)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n  🛑 流水线停止")

    def _print_summary(self, result: dict):
        """打印单次流水线汇总"""
        print(f"\n{'─'*55}")
        print(f"  📊 本次流水线汇总")
        print(f"{'─'*55}")
        for step in result["steps"]:
            icon = {1: "📷", 2: "🔍", 3: "📐", 4: "🦾"}.get(step["step"], "•")
            print(f"  {icon} {step['name']:<12} {step['latency_ms']:>6.1f}ms  "
                  f"| {step['output']}")
        print(f"{'─'*55}")
        total = result.get("total_latency_ms", 0)
        status = "✅ 抓取成功" if result["success"] else "❌ 抓取失败"
        print(f"  ⏱  总延迟: {total:.1f}ms  |  结果: {status}")
        print(f"{'─'*55}\n")

    def shutdown(self):
        self.controller.shutdown()
        self.bridge.shutdown()


# ============================================================
# 🏃  主入口
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Era 2 视觉抓取流水线",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 纯仿真 (Windows only)
  python era2_pipeline.py --mode sim

  # 单张图片测试
  python era2_pipeline.py --mode test --image ./test_chip.jpg

  # 完整流水线 (需要 WSL + ROS2)
  python era2_pipeline.py --mode real --source camera

  # 摄像头实时循环
  python era2_pipeline.py --mode sim --source camera --loop
        """
    )
    parser.add_argument('--mode', type=str, default='sim',
                        choices=['sim', 'real', 'test'],
                        help='运行模式 (默认: sim)')
    parser.add_argument('--source', type=str, default='sim',
                        help='图像来源: sim/camera/图片路径')
    parser.add_argument('--image', type=str, default=None,
                        help='测试图片路径 (--mode test 时使用)')
    parser.add_argument('--loop', action='store_true',
                        help='循环模式')
    parser.add_argument('--interval', type=float, default=3.0,
                        help='循环间隔 (秒)')

    args = parser.parse_args()

    # 确定图像来源
    if args.image:
        source = args.image
    elif args.source == 'camera':
        source = 'camera'
    elif args.mode == 'test' and not args.image:
        print("⚠️  测试模式需要 --image 参数")
        print("   python era2_pipeline.py --mode test --image test.jpg")
        return
    else:
        source = 'sim'

    # 启动流水线
    pipeline = Era2Pipeline(mode=args.mode)

    try:
        if args.loop:
            pipeline.run_loop(source, args.interval)
        else:
            result = pipeline.run_once(source)
            pipeline._print_summary(result)
    except KeyboardInterrupt:
        print("\n  🛑 用户中断")
    finally:
        pipeline.shutdown()


if __name__ == '__main__':
    main()
