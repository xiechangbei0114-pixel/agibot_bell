#!/usr/bin/env python3
"""Panda 机械臂 Python 控制 —— pymoveit2"""

import rclpy
import time
from rclpy.node import Node
from pymoveit2 import MoveIt2

PANDA_JOINTS = [
    'panda_joint1', 'panda_joint2', 'panda_joint3',
    'panda_joint4', 'panda_joint5', 'panda_joint6', 'panda_joint7'
]


class PandaMover(Node):
    def __init__(self):
        super().__init__('panda_mover')
        self.moveit2 = MoveIt2(
            node=self,
            joint_names=PANDA_JOINTS,
            base_link_name='panda_link0',
            end_effector_name='panda_link8',
            group_name='panda_arm',
        )
        self.get_logger().info('Panda Mover ready')

    def move_joint(self):
        """关节空间运动：直接指定 7 个关节弧度"""
        self.get_logger().info('=== Test 1: Joint-space ===')
        # 7 个关节依次: [j1, j2, j3, j4, j5, j6, j7]
        joint_angles = [0.0, -0.785, 0.0, -2.0, 0.0, 1.5, 0.0]
        self.moveit2.move_to_configuration(joint_angles)
        self.moveit2.wait_until_executed()
        self.get_logger().info('Test 1 done')

    def move_pose(self):
        """笛卡尔空间：末端飞到 xyz 坐标"""
        self.get_logger().info('=== Test 2: Cartesian-space ===')
        self.moveit2.move_to_pose(
            position=[0.35, 0.20, 0.50],
            quat_xyzw=[0.0, 0.0, 0.0, 1.0],  # 无旋转
            frame_id='panda_link0',
        )
        self.moveit2.wait_until_executed()
        self.get_logger().info('Test 2 done')

    def move_three_points(self):
        """三点路径：模拟取料→过渡→放料"""
        self.get_logger().info('=== Test 3: Three-point path ===')
        points = [
            (0.35, -0.2, 0.45),
            (0.35, 0.2, 0.45),
            (0.25, 0.0, 0.35),
        ]
        for x, y, z in points:
            self.get_logger().info(f'Moving to ({x}, {y}, {z})')
            self.moveit2.move_to_pose(
                position=[x, y, z],
                quat_xyzw=[0.0, 0.0, 0.0, 1.0],
                frame_id='panda_link0',
            )
            self.moveit2.wait_until_executed()
        self.get_logger().info('Test 3 done')


def main():
    rclpy.init()
    mover = PandaMover()

    print()
    print('=' * 50)
    print('  Panda Arm Python Control')
    print('  1. Joint-space  -> 2. Cartesian  -> 3. Path')
    print('=' * 50)
    print()

    time.sleep(2.0)

    try:
        mover.move_joint()
        time.sleep(1.0)
        mover.move_pose()
        time.sleep(1.0)
        mover.move_three_points()
        print()
        print('All done!')
    except Exception as e:
        mover.get_logger().error(f'Error: {e}')

    rclpy.shutdown()


if __name__ == '__main__':
    main()
