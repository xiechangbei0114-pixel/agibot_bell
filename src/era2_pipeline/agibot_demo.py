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

        self.get_logger().info(f'📦 #{self.part_id} {ptype} 到达 '
                              f'(偏移 x:{x_offset:.3f} y:{y_offset:.3f})')


class PickPlaceArm(Node):
    """模拟机械臂：订阅来料 → 执行抓取 → 上报 MES"""

    def __init__(self):
        super().__init__('pick_place_arm')
        self.sub = self.create_subscription(
            String, 'parts_detected', self.on_part, 10
        )
        self.mes_pub = self.create_publisher(String, 'mes_report', 10)
        self.progress_pub = self.create_publisher(String, 'pick_progress', 10)

        self.busy = False
        self.get_logger().info('🦾 机械臂就绪，等待来料...')

    def on_part(self, msg):
        if self.busy:
            self.get_logger().warn('⏳ 机械臂忙碌，跳过本次')
            return
        self.busy = True

        part_id, ptype, dx, dy = msg.data.split('|')
        self.get_logger().info(f'🎯 收到 #{part_id} {ptype}')

        # 多线程执行不阻塞回调
        t = threading.Thread(target=self.execute_pick, args=(part_id, ptype))
        t.start()

    def execute_pick(self, part_id, ptype):
        try:
            self.publish_progress(part_id, 'approach', '靠近工件')
            time.sleep(0.5)

            self.publish_progress(part_id, 'grasp', '抓取中')
            time.sleep(0.3)

            # 模拟随机失败
            if random.random() < 0.1:
                raise RuntimeError('抓取失败：工件滑落')

            self.publish_progress(part_id, 'lift', '抬起工件')
            time.sleep(0.3)

            self.publish_progress(part_id, 'place', '放料到传送带')
            time.sleep(0.4)

            self.get_logger().info(f'✅ #{part_id} {ptype} 完成')
            self.report_mes(part_id, 'OK', ptype, '抓取成功')

        except Exception as e:
            self.get_logger().error(f'❌ #{part_id} 失败: {e}')
            self.report_mes(part_id, 'FAIL', ptype, str(e))

        self.busy = False

    def publish_progress(self, part_id, stage, desc):
        msg = String()
        msg.data = f'{part_id}|{stage}|{desc}'
        self.progress_pub.publish(msg)

    def report_mes(self, part_id, status, ptype, note):
        msg = String()
        msg.data = f'{part_id}|{status}|{ptype}|{note}'
        self.mes_pub.publish(msg)


class MESReporter(Node):
    """模拟 MES 系统：记录所有产线事件"""

    def __init__(self):
        super().__init__('mes_reporter')
        self.sub = self.create_subscription(
            String, 'mes_report', self.on_report, 10
        )
        self.sub_progress = self.create_subscription(
            String, 'pick_progress', self.on_progress, 10
        )
        self.stats = {'OK': 0, 'FAIL': 0}
        self.get_logger().info('📊 MES 系统就绪，等待报告...')

    def on_report(self, msg):
        part_id, status, ptype, note = msg.data.split('|')
        self.stats[status] = self.stats.get(status, 0) + 1
        total = sum(self.stats.values())
        rate = self.stats['OK'] / total * 100
        self.get_logger().info(f'📋 MES #{part_id}: {status} | '
                              f'{ptype} | {note} | '
                              f'良率 {rate:.1f}% ({self.stats["OK"]}/{total})')

    def on_progress(self, msg):
        part_id, stage, desc = msg.data.split('|')
        self.get_logger().info(f'  ⚙️ #{part_id} {stage}: {desc}')


def main():
    rclpy.init()
    conveyor = ConveyorBelt()
    arm = PickPlaceArm()
    mes = MESReporter()

    print()
    print('=' * 55)
    print('  3C 产线上下料仿真 Demo')
    print('  Topic: /parts_detected  (来料)')
    print('  Topic: /mes_report      (MES)')
    print('  Topic: /pick_progress   (进度)')
    print('=' * 55)
    print()

    try:
        rclpy.spin(conveyor)
    except KeyboardInterrupt:
        print('\n🛑 产线停止')

    conveyor.destroy_node()
    arm.destroy_node()
    mes.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
