#!/usr/bin/env python3
"""
机械臂执行节点：接收 VLA 推理结果 → 控制 Panda 执行

这是"云端 VLA → 本地执行"架构中的本地执行端。
订阅 /vla_pose 拿到抓取位姿，用 MoveIt2 控制 Panda 执行。

用法：
  # 终端 1: 启动 Panda 仿真
  ros2 launch panda_moveit_config panda_gazebo.launch.py
  
  # 终端 2: 启动 VLA 模拟
  python3 cloud_vla_bridge/simulate_vla.py
  
  # 终端 3: 启动执行器（本脚本）
  python3 cloud_vla_bridge/panda_executor.py
  
  # 终端 4: 触发来料（产线 Demo 或手动发）
  ros2 topic pub /parts_detected std_msgs/msg/String "data: '1|CPU芯片|0.02|-0.01'"
"""

import rclpy
import time
import threading
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from pymoveit2 import MoveIt2

PANDA_JOINTS = [
    'panda_joint1', 'panda_joint2', 'panda_joint3',
    'panda_joint4', 'panda_joint5', 'panda_joint6', 'panda_joint7'
]


class PandaExecutor(Node):
    """
    VLA 执行器：
      1. 订阅 /vla_pose（VLA 推理的抓取位姿）
      2. 订阅 /vla_inference_log（推理日志）
      3. 用 MoveIt2 控制 Panda 执行抓取
      4. 发布到 /mes_report（产线记录）
    """

    def __init__(self):
        super().__init__('panda_executor')
        
        # MoveIt2 初始化
        self.moveit2 = MoveIt2(
            node=self,
            joint_names=PANDA_JOINTS,
            base_link_name='panda_link0',
            end_effector_name='panda_link8',
            group_name='panda_arm',
        )
        
        # 等待 MoveIt2 就绪
        time.sleep(2.0)
        
        # 订阅 VLA 推理结果
        self.pose_sub = self.create_subscription(
            PoseStamped, 'vla_pose', self.on_vla_pose, 10
        )
        self.log_sub = self.create_subscription(
            String, 'vla_inference_log', self.on_vla_log, 10
        )
        
        # 发布执行结果到 MES
        self.mes_pub = self.create_publisher(String, 'mes_report', 10)
        self.progress_pub = self.create_publisher(String, 'pick_progress', 10)
        
        # 执行状态
        self.busy = False
        self.current_part_id = None
        self.current_ptype = None
        
        self.get_logger().info('🦾 Panda 执行器就绪，等待 VLA 推理结果...')

    def on_vla_log(self, msg):
        """记录 VLA 推理日志"""
        parts = msg.data.split('|')
        if parts[1] == 'VLA_FAIL':
            self.get_logger().warn(f'⚠️ VLA 推理失败: #{parts[0]} {parts[2]} - {parts[3]}')
            # VLA 失败 → 这里可以触发兜底（第二层视觉定位）
            self.trigger_fallback(parts[0], parts[2])

    def on_vla_pose(self, msg):
        """收到 VLA 推理的抓取位姿 → 执行"""
        if self.busy:
            self.get_logger().warn('⏳ 机械臂忙碌中，跳过本次指令')
            return
        
        # 改用线程执行，不阻塞回调
        t = threading.Thread(target=self.execute_grasp, args=(msg,))
        t.start()

    def execute_grasp(self, pose_msg):
        """执行抓取动作"""
        self.busy = True
        
        x = pose_msg.pose.position.x
        y = pose_msg.pose.position.y
        z = pose_msg.pose.position.z
        
        self.get_logger().info(f'🎯 执行抓取: ({x:.3f}, {y:.3f}, {z:.3f})')
        
        try:
            # Step 1: 移动到抓取位置上方（预接近位）
            self.publish_progress('approach', '靠近取料位')
            pre_x, pre_y, pre_z = x, y, z + 0.15  # 上方 15cm
            self.moveit2.move_to_pose(
                position=[pre_x, pre_y, pre_z],
                quat_xyzw=[0.0, 0.0, 0.0, 1.0],
                frame_id='panda_link0',
            )
            self.moveit2.wait_until_executed()
            self.get_logger().info('   ✅ 预接近到位')
            
            # Step 2: 下降到抓取位置
            self.publish_progress('grasp', '下降到抓取位')
            self.moveit2.move_to_pose(
                position=[x, y, z],
                quat_xyzw=[0.0, 0.0, 0.0, 1.0],
                frame_id='panda_link0',
            )
            self.moveit2.wait_until_executed()
            self.get_logger().info('   ✅ 抓取到位')
            
            time.sleep(0.5)  # 模拟夹爪闭合
            
            # Step 3: 抬起（取料完成）
            self.publish_progress('lift', '抬起工件')
            lift_z = z + 0.20
            self.moveit2.move_to_pose(
                position=[x, y, lift_z],
                quat_xyzw=[0.0, 0.0, 0.0, 1.0],
                frame_id='panda_link0',
            )
            self.moveit2.wait_until_executed()
            self.get_logger().info('   ✅ 取料完成')
            
            # Step 4: 移动到放料位
            self.publish_progress('place', '移动到放料位')
            self.moveit2.move_to_pose(
                position=[0.25, 0.0, 0.35],
                quat_xyzw=[0.0, 0.0, 0.0, 1.0],
                frame_id='panda_link0',
            )
            self.moveit2.wait_until_executed()
            self.get_logger().info('   ✅ 放料到位')
            
            # 上报 MES：成功
            if self.current_part_id and self.current_ptype:
                msg = String()
                msg.data = f'{self.current_part_id}|OK|{self.current_ptype}|VLA抓取成功'
                self.mes_pub.publish(msg)
                self.get_logger().info(f'✅ #{self.current_part_id} 完成')
            
        except Exception as e:
            self.get_logger().error(f'❌ 执行失败: {e}')
            if self.current_part_id and self.current_ptype:
                msg = String()
                msg.data = f'{self.current_part_id}|FAIL|{self.current_ptype}|执行异常'
                self.mes_pub.publish(msg)
        
        self.busy = False
        self.current_part_id = None
        self.current_ptype = None

    def trigger_fallback(self, part_id, ptype):
        """VLA 失败后的兜底（第二层：视觉定位重试）"""
        self.get_logger().warn(f'🔄 触发第二层兜底: 视觉定位重试 #{part_id}')
        
        # 这里可以集成 YOLO + 6D 位姿估算
        # 当前简化：用固定位姿模拟视觉定位成功
        self.get_logger().info('   📷 视觉定位：YOLO 检测到工件 → 6D 位姿估算')
        
        # 模拟视觉定位输出（比 VLA 更精确）
        fallback_x, fallback_y, fallback_z = 0.42, 0.02, 0.30
        
        pose_msg = PoseStamped()
        pose_msg.header.frame_id = 'panda_link0'
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.pose.position.x = fallback_x
        pose_msg.pose.position.y = fallback_y
        pose_msg.pose.position.z = fallback_z
        pose_msg.pose.orientation.w = 1.0
        
        self.get_logger().info(f'   ✅ 视觉定位成功: ({fallback_x:.3f}, {fallback_y:.3f})')
        self.current_part_id = part_id
        self.current_ptype = ptype
        self.execute_grasp(pose_msg)

    def publish_progress(self, stage, desc):
        """发布执行进度"""
        msg = String()
        pid = self.current_part_id or '?'
        msg.data = f'{pid}|{stage}|{desc}'
        self.progress_pub.publish(msg)


def main():
    rclpy.init()
    node = PandaExecutor()
    
    print()
    print('=' * 55)
    print('  🦾 Panda VLA 执行器')
    print('  订阅: /vla_pose (VLA 推理结果)')
    print('  订阅: /vla_inference_log (推理日志)')
    print('  发布: /mes_report (产线记录)')
    print('  发布: /pick_progress (执行进度)')
    print('=' * 55)
    print()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\n🛑 执行器停止')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
