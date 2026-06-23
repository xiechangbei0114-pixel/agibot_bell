# Week 1 · 搞懂旧范式（06.17 — 06.23）

> 本周目标：理解 Era 2（模块化规划时代）的核心概念。这不是考古——Era 2 仍是工业主流，也是 Era 3/4 VLA 模型的兜底层。

## 范式背景

```
Era 1 (~2015前)         Era 2 (2015-2024)         Era 3 (2023-2025)       Era 4 (2025-2026)
示教器+PLC+固定轨迹  →  ROS+MoveIt+IK/RRT    →   VLA 端到端          →   世界模型
                       🔥 当前工业主流！         头部试点中              论文阶段
                       = CV 里的 YOLOv8         = CV 里的 SAM          = CV 里的 GPT-4V
```

## 本周每日主题

| 天 | 主题 | 年代标注 | 状态 | 核心产出 |
|:---:|:---|:---:|:---:|:---|
| 1 | 机器人分类 | 全年代 | 📝 | 分类脑图 |
| 2 | 四层控制架构 | Era 1/2 | 📝 | 架构图 + 思考：VLA 取代了哪层？ |
| 3 | ROS2 通信机制 | Era 2 | 📝 | Topic/Service/Action 对比表 |
| 4 | 环境安装 | Era 2 | ✅ | WSL2+ROS2+MoveIt2 全栈 |
| 5 | FK/IK + 仿真工具 | Era 1/2 | 📝 | 思考：VLA 是不是隐式学了 IK？ |
| 6 | Panda Python 控制 | Era 2 | ✅ | panda_move.py 三组运动 |
| 7 | 每周复盘 + 范式对比 | 跨年代 | 📝 | 范式演进图 v1.0 |

## 📂 本周仿真代码清单

| 文件 | 说明 | 运行方式 | 硬件要求 |
|:---|:---|:---|:---:|
| `panda_move.py` | MoveIt2 Panda 关节/笛卡尔/三点路径控制 | `python3 panda_move.py` | ROS2 + Panda 仿真 |
| `agibot_demo.py` | 3C 产线上下料 Topic 通信仿真 (3 Nodes) | `python3 agibot_demo.py` | ROS2 |
| **`fk_ik_simulator.py`** 🆕 | **纯 Python FK/IK 仿真器** — 2 连杆双解 + 5-DOF 数值 IK + 动画 | `python fk_ik_simulator.py` | **无**（仅需 numpy+matplotlib） |
| **`two_link_arm_sim.html`** 🆕 | **浏览器 FK/IK 交互仿真** — 拖拽目标点看实时 IK 双解 | 双击用浏览器打开 | **无**（纯前端 Three.js 风格） |

## 🎮 仿真练习

### 练习 1: FK 直觉（用 `two_link_arm_sim.html`）
1. 打开 HTML，切换到 **FK 模式**
2. 调节 θ₁ 到 90°，观察末端位置
3. 再调 θ₂ 到 -90°，观察末端位置变化
4. **思考**：如果 VLA 模型输出的末端位姿超出了机械臂可达范围，底层 MoveIt IK solver 会报什么错？

### 练习 2: IK 双解（用 `two_link_arm_sim.html`）
1. 切换到 **IK 模式**
2. 拖动红色目标到 (0.5, 1.2)
3. 观察蓝色（肘朝上）和绿色（肘朝下，虚线）两套解
4. 拖动目标到不可达区域，观察"❌ 不可达"提示
5. **面试话术**："IK 的多解性意味着 VLA 需要额外约束（如'最短路径''避障'）来选择最优解。"

### 练习 3: 数值 IK（用 `fk_ik_simulator.py`）
```bash
python fk_ik_simulator.py
# 选择 2 → 观察 5-DOF 机械臂的数值 IK 收敛过程
# 特别关注"奇异位姿"下的关节角剧烈变化
```

## 本周通关标准

1. 脱稿讲 5 分钟「从传感器到执行器的完整数据链路」+ 标注每层在 VLA 时代的变化
2. `ros2 topic list` 跑过 ✅
3. Python 脚本让仿真机械臂动起来 ✅
