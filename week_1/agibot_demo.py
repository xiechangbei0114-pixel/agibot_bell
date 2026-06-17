#!/usr/bin/env python3
"""
3C 产线上下料仿真 Demo — 直接可跑，无需 colcon build

架构（三个 Node，两个 Topic）：

  conveyor_belt          pick_place_arm         mes_reporter
  (来料传感器)            (机械臂执行)            (MES上报)
      │                       │                      │
      ├─ /parts_detected ──▶  │                      │
      │   Topic: "零件ID|类型" │                      │
      │                       │ (收到来料→执行抓取)    │
      │                       │                      │
      │                       ├─ /mes_report ──────▶ │
      │                       │   Topic: "ID|结果"    │
      │                       │                      │

用法：
  python3 agibot_demo.py
  # 另开终端：
  ros2 topic echo /parts_detected    # 看来料
  ros2 topic echo /mes_report        # 看 MES 上报
"""

import rclpy
import time
import random
import threading
from rclpy.node import Node
from std_msgs.msg import String


class ConveyorBelt(Node):
    """模拟产线传感器：每 3 秒检测到一个零件，发布到 /parts_detected"""

    def __init__(self):
        super().__init__('conveyor_belt')
        self.pub = self.create_publisher(String, 'parts_detected', 10)
        self.part_id = 0
        self.part_types = ['CPU芯片', '连接器', '螺丝座', '散热片', '电容']
        self.timer = self.create_timer(3.0, self.part_arrived)
        self.get_logger().info('🏭 产线传感器就绪，模拟来料...')

    def part_arrived(self):
        self.part_id += 1
        ptype = random.choice(self.part_types)
        x_offset = random.uniform(-0.05, 0.05)
        y_offset = random.uniform(-0.05, 0.05)

        msg = String()
        msg.data = f'{self.part_id}|{ptype}|{x_offset:.3f}|{y_offset:.3f}'
        self.pub.publish(msg)
        self.get_logger().info(f'📦 来料 #{self.part_id}: {ptype} (偏移: {x_offset:.3f}, {y_offset:.3f})')


class PickPlaceArm(Node):
    """
    模拟机械臂：
      1. 订阅 /parts_detected（收到来料）
      2. 模拟抓取流程（approach → grasp → place）
      3. 发布结果到 /mes_report
    """

    def __init__(self):
        super().__init__('pick_place_arm')
        self.sub = self.create_subscription(String, 'parts_detected', self.on_part, 10)
        self.mes_pub = self.create_publisher(String, 'mes_report', 10)
        self.progress_pub = self.create_publisher(String, 'pick_progress', 10)

        # 模拟成功率
        self.success_rate = 0.92
        self.get_logger().info('🦾 机械臂就绪，等待来料...')

    def on_part(self, msg):
        part_id, ptype, dx, dy = msg.data.split('|')
        self.get_logger().info(f'🔔 收到来料 #{part_id} {ptype}')

        # 异步执行抓取（用线程模拟，不阻塞 Topic 回调）
        t = threading.Thread(target=self.execute_pick, args=(part_id, ptype, dx, dy))
        t.start()

    def execute_pick(self, part_id, ptype, dx, dy):
        """模拟三步抓取流程"""
        stages = [
            ('approach', 1.0, '靠近取料位'),
            ('grasp',    0.5, '夹爪闭合'),
            ('place',    1.5, '移动放料位'),
        ]

        for stage, duration, desc in stages:
            msg = String()
            msg.data = f'{part_id}|{stage}|{desc}'
            self.progress_pub.publish(msg)
            self.get_logger().info(f'   ⏳ [{stage}] {desc}...')
            time.sleep(duration / 2.0)  # 加速演示

        # 结果判断
        success = random.random() < self.success_rate
        result_msg = String()
        if success:
            result_msg.data = f'{part_id}|OK|{ptype}|抓取成功|{int(sum(d for _, d, _ in stages)*1000)}ms'
            self.get_logger().info(f'✅ #{part_id} {ptype} 抓取成功！')
        else:
            result_msg.data = f'{part_id}|FAIL|{ptype}|抓取失败(零件滑落)'
            self.get_logger().warn(f'❌ #{part_id} {ptype} 抓取失败！')

        self.mes_pub.publish(result_msg)


class MESReporter(Node):
    """MES 系统：订阅 /mes_report，记录产线日志"""

    def __init__(self):
        super().__init__('mes_reporter')
        self.sub = self.create_subscription(String, 'mes_report', self.on_report, 10)
        self.total = 0
        self.success = 0
        self.get_logger().info('📊 MES 系统上线，监听生产数据...')

    def on_report(self, msg):
        parts = msg.data.split('|')
        self.total += 1
        status = parts[1]
        if status == 'OK':
            self.success += 1

        rate = self.success / self.total * 100 if self.total > 0 else 0
        self.get_logger().info(
            f'📊 MES 记录 | 总计: {self.total} | 成功: {self.success} | '
            f'良率: {rate:.1f}% | 本条: {msg.data}'
        )


def main():
    rclpy.init()

    conveyor = ConveyorBelt()
    arm = PickPlaceArm()
    mes = MESReporter()

    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(conveyor)
    executor.add_node(arm)
    executor.add_node(mes)

    print()
    print('=' * 55)
    print('  🏭 3C 产线上下料 Demo')
    print('  Topic 通信: /parts_detected → /pick_progress → /mes_report')
    print('  按 Ctrl+C 停止')
    print('=' * 55)
    print()

    try:
        executor.spin()
    except KeyboardInterrupt:
        print('\n🛑 产线停机')
    finally:
        executor.shutdown()
        conveyor.destroy_node()
        arm.destroy_node()
        mes.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
