# Day 6 · Panda 仿真 + Python 控制

> 📎 资源：MoveIt2 Python API (moveit.picknik.ai) / cobots2024 Jeju AI Tutorial / Aleksandar Haber 教程
> 🕐 预计用时：1-2h

---

## 1. 启动仿真（已跑通）

```bash
source /opt/ros/humble/setup.bash
source ~/robot_ws/install/setup.bash
ros2 launch moveit2_tutorials demo.launch.py
```

验证环境正常的 Python 脚本：

```python
#!/usr/bin/env python3
"""环境验证脚本：确认 ROS2 + MoveIt2 跑通"""
import rclpy
from rclpy.node import Node

class PandaCheck(Node):
    def __init__(self):
        super().__init__('panda_check')
        self.get_logger().info('ROS2 环境正常！')
        self.get_logger().info('Panda 节点已启动，准备接收运动指令。')

def main():
    rclpy.init()
    node = PandaCheck()
    rclpy.spin_once(node, timeout_sec=1)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

## 2. 用 MoveItPy 控制 Panda（进阶脚本）

这是基于 MoveIt2 官方 Python API (`moveit_py`) 的完整运动脚本。

```python
#!/usr/bin/env python3
"""Panda 运动控制脚本 —— 给定目标位姿，规划并执行运动"""
import rclpy
import sys
from moveit.planning import MoveItPy
from moveit_configs_utils import MoveItConfigsBuilder
from geometry_msgs.msg import PoseStamped

def plan_and_execute(robot, planning_component):
    """规划并执行轨迹"""
    plan_result = planning_component.plan()
    if plan_result:
        robot_trajectory = plan_result.trajectory
        robot.execute(robot_trajectory, controllers=[])
        print("✅ 运动完成！")
    else:
        print("❌ 规划失败！检查目标是否在机械臂工作空间内。")

def main():
    rclpy.init()

    # 加载 Panda MoveIt 配置
    moveit_config = (
        MoveItConfigsBuilder(
            robot_name="panda",
            package_name="moveit_resources_panda_moveit_config"
        )
        .robot_description(file_path="config/panda.urdf.xacro")
        .trajectory_execution(file_path="config/gripper_moveit_controllers.yaml")
        .to_moveit_configs()
        .to_dict()
    )

    panda = MoveItPy(node_name="moveit_py_demo", config_dict=moveit_config)
    panda_arm = panda.get_planning_component("panda_arm")

    # —— 方式1：关节空间运动（用预设关节角度）——
    print("=== 测试1：关节空间运动 ===")
    panda_arm.set_start_state(configuration_name="ready")
    panda_arm.set_goal_state(configuration_name="extended")
    plan_and_execute(panda, panda_arm)

    # —— 方式2：笛卡尔空间运动（给定 x/y/z）——
    print("=== 测试2：笛卡尔空间运动 ===")
    panda_arm.set_start_state_to_current_state()

    pose_goal = PoseStamped()
    pose_goal.header.frame_id = "panda_link0"
    pose_goal.pose.orientation.w = 1.0     # 不旋转（w=1 是四元数的单位值）
    pose_goal.pose.position.x = 0.3        # 前方 30 cm
    pose_goal.pose.position.y = 0.0        # 正中间
    pose_goal.pose.position.z = 0.4        # 高度 40 cm

    panda_arm.set_goal_state(
        pose_stamped_msg=pose_goal,
        pose_link="panda_link8"            # 末端夹爪的 frame
    )
    plan_and_execute(panda, panda_arm)

    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### ⚠️ 关键参数解释

| 参数 | 含义 |
|:---|:---|
| `"ready"` | Panda 的伸直归零位姿（预设配置） |
| `"extended"` | Panda 的前伸位姿（预设配置） |
| `panda_link0` | 基座坐标系（参考原点） |
| `panda_link8` | 末端法兰坐标系（夹爪安装位置） |
| `orientation.w = 1.0` | 四元数表示无旋转（夹爪保持竖直朝下） |
| `position.x/y/z` | 末端位置，单位：米 |

---

## 3. plan_and_execute 的执行链路

```
plan_and_execute()
  │
  ├─ IK 求解器 (KDL / Trac-IK)
  │     └─「目标位姿→需要哪些关节角?」
  │
  ├─ 运动规划器 (OMPL / RRTConnect)
  │     └─「从当前角到目标角的无碰撞轨迹」
  │
  ├─ 轨迹执行 (ros2_control / JointTrajectoryController)
  │     └─「轨迹→关节速度/力矩指令→电机转动」
  │
  └─ 实时反馈 (Joint State Topic)
        └─「当前关节角=多少? 到达目标了?」
```

---

## 4. 动手任务

### 基础任务
1. 跑通上面的基础验证脚本（PandaCheck）
2. 改用 MoveItPy 脚本，让 Panda 运动到 3 个不同位置

### 进阶任务
3. 让 Panda 画一个正方形（4 个角点依次运动）
4. 修改 `orientation`，让夹爪旋转 90° 再到达目标

### 调试技巧
```bash
# 看当前关节角度
ros2 topic echo /joint_states

# 看 MoveIt 规划的轨迹
ros2 topic echo /display_planned_path

# 单独跑 IK（不执行）
# 在代码里 plan() 拿到 plan_result 后不调用 execute()
```

---

## 5. 面试自检答案

> **Q: 你调用了 plan_and_execute，从函数调用到关节转动经过了哪些环节？**

**A:** 见上面第 3 部分的链路图。重点说清三个环节：
1. **IK 求解**：把末端位姿反算为关节角度
2. **运动规划**：RRT 算法在 6D 关节空间搜索无碰撞轨迹
3. **轨迹执行**：ros2_control 把轨迹转为电机指令，PID 闭环跟踪

> 💡 加分：知道 plan() 和 execute() 可以分开调用——plan() 只计算不执行（可预览轨迹），execute() 才真正发送指令给硬件。

---

## ✍️ 你的笔记

- 你让 Panda 运动到了哪几个位置？坐标是多少？
- 如果设的目标超出机械臂工作范围（z=2.0），发生了什么？
- 把 `orientation.w` 从 1.0 改成别的值会怎样？（提示：四元数 w=cos(θ/2)）
