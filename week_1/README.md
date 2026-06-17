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

## 本周已完成的实操

- [x] WSL2 + Ubuntu 22.04 安装在 D 盘
- [x] ROS2 Humble 环境 + MoveIt2 + Panda 仿真
- [x] `ros2 topic list` 验证通过
- [x] 产线上下料 Topic 通信 demo（agibot_demo.py）
- [x] Panda Python 关节/笛卡尔/路径控制（panda_move.py）

## 本周通关标准

1. 脱稿讲 5 分钟「从传感器到执行器的完整数据链路」+ 标注每层在 VLA 时代的变化
2. `ros2 topic list` 跑过 ✅
3. Python 脚本让仿真机械臂动起来 ✅
