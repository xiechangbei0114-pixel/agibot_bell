# Day 3 · ROS2 核心概念：Node / Topic / Service / Action

> 📎 资源：ROS2 官方文档 Interfaces 章节 (docs.ros.org) / The Construct ROS2 How-to #5 / 鱼香 ROS 教程
> 🕐 预计用时：1h

---

## 1. 四个概念的定位

```
Node = 进程（谁干活）
Topic = 数据广播（持续发）
Service = 一次问答（问一句答一句）
Action = 异步任务（你要什么 + 做到哪了 + 可取消）
```

| | Topic | Service | Action |
|:---|:---|:---|:---|
| **模式** | Publish/Subscribe | Request/Response | Goal/Feedback/Result |
| **方向** | 单向 | 双向（同步） | 双向（异步 + 持续反馈） |
| **连接** | N: N | 1:1 | 1:1 |
| **阻塞** | 非阻塞 | **阻塞**（客户端等待） | 非阻塞 |
| **耗时** | 持续流 | 毫秒级 | 秒~分钟级 |
| **取消** | ✗ | ✗ | ✓ 可抢占 |
| **ROS 类比** | 广播电台 | 电话问答 | 外卖下单→接单→配送→完成 |

---

## 2. Topic（话题）—— 数据管道

**本质**：发布者持续推送消息，订阅者异步接收。发布者不知道谁在听。

### 什么时候用 Topic？

- 传感器数据流：LiDAR 扫描、相机图像、IMU 数据
- 机器人状态：关节角度、里程计、电池电压
- 控制指令：`/cmd_vel`（AGV 速度指令）

### 命令行实操（在你的 WSL 里跑）

```bash
# 看当前所有话题
ros2 topic list

# 看某个话题的数据
ros2 topic echo /parameter_events

# 看话题发送频率
ros2 topic hz /rosout
```

### Python 示例：发布/订阅

```python
# publisher.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.pub = self.create_publisher(String, 'chatter', 10)
        self.timer = self.create_timer(0.5, self.callback)

    def callback(self):
        msg = String()
        msg.data = 'Hello ROS2!'
        self.pub.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')

rclpy.init()
rclpy.spin(Talker())
```

```python
# subscriber.py  
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.sub = self.create_subscription(String, 'chatter', self.callback, 10)

    def callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')
```

---

## 3. Service（服务）—— 问答调用

**本质**：客户端发请求，**等**服务器返回结果。同步、一次性的 RPC 调用。

### 什么时候用 Service？

- 查询当前状态：「给我现在的关节角度」
- 触发瞬态动作：「保存地图」、「拍张照片」
- 设置参数：「切换夹爪工具」

### ⚠️ 绝对不要用 Service 的场景

**长时间运行的任务**——会阻塞客户端，无法取消，没有进度反馈。用 Action。

### 命令行

```bash
# 列出所有服务
ros2 service list

# 调用一个服务
ros2 service call /spawn turtlesim/srv/Spawn "{x: 2.0, y: 3.0, theta: 0.0, name: 'turtle2'}"
```

---

## 4. Action（动作）—— 长任务引擎

**本质**：建立在 Topic + Service 之上的**状态机**。客户端发起目标（Goal），服务器运行任务期间持续发送进度（Feedback），最终返回结果（Result）。可随时取消。

### Action 的内部结构

```
一个 Action = 2 个 Service + 2 个 Topic
  ├─ Goal Service    → 提交任务
  ├─ Result Service  → 返回结果
  ├─ Feedback Topic  → 持续进度更新
  ├─ Cancel Service  → 取消任务
  └─ Status Topic    → 广播当前状态
```

### 三个终端状态

| 状态 | 含义 |
|:---|:---|
| `SUCCEEDED` | 任务成功完成 |
| `ABORTED` | 任务被中止（出错/不可能完成） |
| `CANCELED` | 任务被客户端主动取消 |

### 什么时候必须用 Action？

- 导航：「开到坐标 (3, 5)，朝向 90°」—— 可能耗时 30s~5 min
- 抓取：MoveIt2 的 `plan_and_execute` —— 规划 + 执行 + 反馈
- 巡检：「在这个区域巡逻，拍照 5 个点」

### 命令行

```bash
# 列出所有 Action
ros2 action list

# 发送一个导航目标
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 2.0}, orientation: {w: 1.0}}}}"
```

---

## 5. 决策树：什么时候用什么？

```
数据是持续产出的数据流？
  └─ YES → Topic

是一次性的快速查询/指令（毫秒级）？
  └─ YES → Service

任务耗时数秒以上、需要进度反馈、可能需要取消？
  └─ YES → Action
```

---

## 6. 面试自检答案

> **Q: 为什么机器人抓取用 Action 而不是 Topic？你的 AGV 里和 MES 通信类似哪种？**

**A:**
1. **抓取为什么用 Action？**
   - 规划轨迹可能失败 → 需要知道结果是 SUCCEEDED 还是 ABORTED
   - 运动过程中需要进度反馈 → 关节当前转了多少度
   - 可能中途要取消 → 碰撞预警触发紧急停止

2. **AGV 和 MES 通信类似哪种？**
   - AGV 调度给 MES 上报任务状态 → 类似 **Topic**（状态持续广播）
   - MES 询问 AGV 「你现在在哪」 → 类似 **Service**（一次查询一次应答）
   - AGV 接到「从 A 送到 B」的任务 → 类似 **Action**（目标 + 进度 + 结果 + 可取消）

> **Q: ROS2 的 DDS 和 MQTT 有什么区别？**

| | DDS | MQTT |
|:---|:---|:---|
| **架构** | 去中心化 P2P | 中心化 Broker |
| **发现** | 自动发现（UDP 组播） | 需要 Broker 注册 |
| **实时性** | 低延迟（~100 μs） | 毫秒级延迟（经 Broker） |
| **QoS** | 精细控制（截止时间/可靠性/寿命） | 3 级 QoS |
| **适用** | 机器人内部通信（有线、实时） | IoT、跨网络、云端 |

ROS2 默认用 DDS 是因为机器人内部需要**低延迟、去中心化、自动发现**的实时通信。DDS 被设计用于安全关键系统（可达 ISO 26262 ASIL-D）。但跨无线网络/云端时 MQTT 更合适。

---

## ✍️ 你的笔记

### Topic 练习
用 `ros2 topic list` 和 `ros2 topic echo` 查看你的 Panda 仿真里有哪些话题在跑。写出你看到的 5 个话题名称。

### Service 练习
用 `ros2 service list` 查看可用的服务。试着调用一个。

### Action 练习
Panda 仿真中 `plan_and_execute` 是一个 Action。你能用 `ros2 action list` 找到它吗？
