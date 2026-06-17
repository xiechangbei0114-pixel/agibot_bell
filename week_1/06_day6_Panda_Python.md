# Day 6 · Panda 仿真 + Python 控制（06.22）

## 环境 ✅ 已提前完成

MoveIt2 + Panda 仿真环境于 06.17 提前搭完，详见 [install_ros.md](install_ros.md)。

## 今天要做的

### 1. 启动 Panda 仿真（已跑通）

```bash
source /opt/ros/humble/setup.bash
source ~/robot_ws/install/setup.bash
ros2 launch moveit2_tutorials demo.launch.py
```

### 2. 写 Python 控制脚本

参考模板（来自学习计划）：

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class PandaController(Node):
    def __init__(self):
        super().__init__('panda_controller')
        self.get_logger().info('Panda 控制器已启动！')

def main():
    rclpy.init()
    node = PandaController()
    rclpy.spin_once(node, timeout_sec=1)
    print("✅ ROS2 + MoveIt2 环境正常！")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 3. 下一步挑战

修改参数，让 Panda 运动到不同位姿（x, y, z 坐标）

## ✍️ 你的笔记 + 运行截图



## 🔍 面试自检

> 「你调用了 plan_and_execute，从函数调用到关节转动经过了哪些环节？」

---

🕐 Python 实操预计：1-2h | 📎 moveit.picknik.ai Python API 教程
