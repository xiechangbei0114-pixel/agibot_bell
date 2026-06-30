#!/usr/bin/env python3
"""
模拟云端 VLA 推理节点

工作原理：
  1. 订阅 /parts_detected（来料信号，来自 agibot_demo.py 的 conveyor_belt）
  2. "推理" → 生成目标抓取位姿（实际是根据零件偏移量算一个合理的抓取点）
  3. 发布到 /vla_pose（供机械臂执行）

这个脚本模拟了 VLA 模型的行为，但不需要 GPU。
当你有了云端 GPU 后，把这里的"随机生成位姿"换成调用云端 API 即可。

用法：
  # 终端 1: 启动 Panda 仿真
  ros2 launch panda_moveit_config panda_gazebo.launch.py
  
  # 终端 2: 启动产线 Demo
  python3 week_1/agibot_demo.py
  
  # 终端 3: 启动 VLA 模拟（本脚本）
  python3 cloud_vla_bridge/simulate_vla.py
  
  # 终端 4: 启动机械臂执行节点
  python3 cloud_vla_bridge/panda_executor.py
"""

import rclpy
import math
import random
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped


class SimulatedVLA(Node):
    """模拟云端 VLA 模型推理"""

    def __init__(self):
        super().__init__('simulated_vla')
        
        # 订阅来料信号
        self.sub = self.create_subscription(
            String, 'parts_detected', self.on_part, 10
        )
        
        # 发布 VLA 推理结果（抓取位姿）
        self.pose_pub = self.create_publisher(PoseStamped, 'vla_pose', 10)
        
        # 也发布文本格式的推理日志（方便看）
        self.log_pub = self.create_publisher(String, 'vla_inference_log', 10)
        
        # 模拟 VLA 的成功率（跟方案里的 ~85-92% 一致）
        self.vla_success_rate = 0.88
        
        self.get_logger().info('🧠 云端 VLA 模型已加载（GO-2 模拟版）')
        self.get_logger().info('   等待来料信号...')

    def on_part(self, msg):
        """收到来料 → 执行推理"""
        part_id, ptype, dx, dy = msg.data.split('|')
        dx, dy = float(dx), float(dy)
        
        self.get_logger().info(f'🔍 VLA 推理中... #{part_id} {ptype}')
        
        # --- 模拟 Action CoT（动作思维链）---
        self.get_logger().info('   ├─ Step 1: 场景理解 → 识别工件类型 ✓')
        self.get_logger().info(f'   ├─ Step 2: 目标定位 → 偏移 ({dx:.3f}, {dy:.3f})')
        
        # 模拟推理耗时
        import time
        time.sleep(0.5)
        
        # 模拟 VLA 可能失败
        if random.random() > self.vla_success_rate:
            self.get_logger().warn(f'   └─ ❌ VLA 推理失败：来料偏移超出泛化范围')
            fail_msg = String()
            fail_msg.data = f'{part_id}|VLA_FAIL|{ptype}|偏移超出泛化范围'
            self.log_pub.publish(fail_msg)
            return
        
        # --- 生成抓取位姿 ---
        # 基准位置（Panda 工作空间内）
        base_x, base_y, base_z = 0.45, 0.0, 0.30
        
        # 根据来料偏移调整抓取点（模拟 VLA 的泛化能力）
        grasp_x = base_x + dx
        grasp_y = base_y + dy
        grasp_z = base_z
        
        # 发布位姿
        pose_msg = PoseStamped()
        pose_msg.header.frame_id = 'panda_link0'
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        
        pose_msg.pose.position.x = grasp_x
        pose_msg.pose.position.y = grasp_y
        pose_msg.pose.position.z = grasp_z
        
        # 四元数：末端朝下（适合抓取）
        pose_msg.pose.orientation.x = 0.0
        pose_msg.pose.orientation.y = 0.0
        pose_msg.pose.orientation.z = 0.0
        pose_msg.pose.orientation.w = 1.0
        
        self.pose_pub.publish(pose_msg)
        
        # 发布推理日志
        log_msg = String()
        log_msg.data = f'{part_id}|VLA_OK|{ptype}|位姿({grasp_x:.3f},{grasp_y:.3f},{grasp_z:.3f})'
        self.log_pub.publish(log_msg)
        
        self.get_logger().info(
            f'   └─ ✅ VLA 推理完成 → 抓取位姿 ({grasp_x:.3f}, {grasp_y:.3f}, {grasp_z:.3f})'
        )
        self.get_logger().info('   └─ Step 3: Action CoT → 靠近→对准→抓取→抬起 ✓')


def main():
    rclpy.init()
    node = SimulatedVLA()
    
    print()
    print('=' * 55)
    print('  🧠 云端 VLA 推理模拟器')
    print('  订阅: /parts_detected')
    print('  发布: /vla_pose (抓取位姿)')
    print('  发布: /vla_inference_log (推理日志)')
    print('  成功率: 88%（模拟真实 VLA 泛化能力）')
    print('=' * 55)
    print()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\n🛑 VLA 推理服务停止')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
