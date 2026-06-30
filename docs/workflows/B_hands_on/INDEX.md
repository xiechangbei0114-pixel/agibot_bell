---
name: workflow-hands-on
description: 🔧 实操流水线 — ROS2→MoveIt2→VLA仿真→Genie Sim源码→云端桥接
metadata:
  type: reference
---

# 🔧 工作流 B：实操流水线

> 目标：面试官问"做过什么"时，打开架构图讲 2 分钟完整流水线

---

## 📋 总览

```
                  Era 2 流水线                          Era 3 VLA
┌─────────────────────────────┐    ┌─────────────────────────────┐
│ Windows (你的老本行)         │    │ 云GPU (AutoDL / isaaclab)  │
│  YOLO / OpenCV / 相机       │    │  OpenPI / GR00T 推理        │
│       │                     │    │       │                     │
│       ▼ ROS2 Topic          │    │       ▼ WebSocket           │
│  /parts_detected            │    │  /vla_inference_log         │
│       │                     │    │       │                     │
│       ▼ WSL (ROS2)          │    │       ▼ WSL (ROS2)          │
│  Panda MoveIt2 / Gazebo     │    │  Panda Executor + 兜底      │
│       │                     │    │       │                     │
│       ▼ 四级兜底            │    │       ▼ 四级兜底            │
│  ① VLA → ② 视觉重试         │    │  ① VLA → ② 视觉重试         │
│  ③ 力控 → ④ 报警           │    │  ③ 力控 → ④ 报警           │
└─────────────────────────────┘    └─────────────────────────────┘
```

---

## 🗂️ 代码结构

```
src/
├── era2_pipeline/           ← Era 2: 视觉感知 + ROS2 + 机械臂控制
│   ├── agibot_demo.py       产线Topic通信 (ROS2 pub/sub)
│   ├── panda_move.py        Panda MoveIt2 控制
│   ├── fk_ik_simulator.py   FK/IK 运动学仿真
│   ├── visual_pipeline.py   视觉抓取完整流水线 (YOLO→位姿→IK→执行)
│   ├── interactive_pipeline.py 交互式流水线调参
│   └── two_link_arm_sim.html  二连杆可视化 (浏览器)
│
├── era3_vla/                ← Era 3: VLA 端到端推理 + 云端桥接
│   ├── vla_inference_demo.py     VLA推理 (完整版, numpy)
│   ├── vla_inference_lite.py     VLA推理 (轻量版, 纯Python)
│   ├── vla_pipeline_sim.py       VLA流水线量化对比
│   ├── data_flywheel_sim.py      冷启动数据飞轮
│   ├── rl_baseline_demo.py       RL基线对比
│   ├── rl_demo_result.png
│   └── cloud_bridge/            云端VLA→本地Panda
│       ├── simulate_vla.py       VLA推理模拟器 (ROS2节点)
│       ├── panda_executor.py     机械臂执行器 + 兜底
│       ├── vla_cloud_bridge.py   云端桥接 (WebSocket)
│       ├── deploy_to_autodl.md   云端部署指南
│       └── README.md
│
├── tools/                   ← 工具
│   ├── roi_calculator.py        ROI计算器
│   ├── scenario_visualizer.py   场景可视化
│   ├── vla_failure_diagnoser.py VLA翻车诊断
│   ├── integration_checker.py   整合检查
│   └── hand_eye_calibration_sim.py 手眼标定仿真
```

---

## 🏗️ 实操任务 (按优先级)

| 优先级 | 实操 | 代码位置 | 面试价值 |
|:---:|:---|---:|:---:|
| 🔴 **P0** | Era 2 完整流水线 | `visual_pipeline.py` | ⭐⭐⭐⭐⭐ |
| 🔴 **P0** | Era 3 模拟VLA+Panda | `cloud_bridge/simulate_vla.py` + `panda_executor.py` | ⭐⭐⭐⭐⭐ |
| 🔴 **P0** | 四级兜底Demo | 整合所有 | ⭐⭐⭐⭐⭐ |
| 🟡 P1 | Genie Sim 源码精读 | `genie_sim_study_guide.md` | ⭐⭐⭐ |
| 🟡 P1 | 去公司看智元真机 | — | ⭐⭐⭐⭐⭐ |
| 🟢 P2 | 云端VLA桥接 | `vla_cloud_bridge.py` | ⭐⭐⭐ |

---

## 🔍 Genie Sim 源码精读 (方案岗必看)

> 完整精读 → [`genie_sim_study_guide.md`](genie_sim_study_guide.md)

从 76,000 行中精选 ~1,500 行核心:

| 文件 | 行数 | 方案岗价值 |
|:---|---:|:---|
| `api_core.py` | 45KB | Genie Sim 中央API, 理解"Genie Sim 能干什么" |
| `task_benchmark.py` | 16KB | observe→predict→step 评测循环 |
| `omniagent.py` | 47KB | **你的四级兜底的代码实现** |
| `llm_scene_generator.py` | 4KB | 自然语言→仿真场景 |
| `base.py / pipolicy.py` | — | 策略抽象层 (Pi0.5/GR00T同一接口) |

**面试话术：**
> "我看了 Genie Sim 的 OmniAgent 源码，它把任务分解为 approach→grasp→place→insert 原子动作，每步有 retry 机制——这和我方案里的四级兜底设计思路一致。"

---

## 🛠️ WSL 环境能力边界

| 能做什么 | 不能做什么 |
|:---|---:|
| ROS2 Humble + MoveIt2 + Panda 仿真 ✅ | Genie Sim (需 RTX 4080+) ❌ |
| Python 控制机械臂运动规划 ✅ | 真实 VLA 推理 (需云 GPU) ❌ |
| 通过 ROS2 Topic 跨 Windows-WSL 通信 ✅ | |
| 模拟 VLA 结果在 Panda 上执行 ✅ | |

---

## 📎 关联文档

| 文档 | 位置 |
|:---|---:|
| 云端部署指南 | `src/era3_vla/cloud_bridge/deploy_to_autodl.md` |
| Genie Sim 精读 | `genie_sim_study_guide.md` |
| Isaac Sim 笔记 | `isaac_sim_notes.md` |
