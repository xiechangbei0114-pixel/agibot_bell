# 🔧 实操流水线 · B_hands_on

> 入口 | [Era 2 流水线](01_era2_pipeline/code/) | [Era 3 VLA](02_era3_vla/code/) | [仿真参考](04_simulation/) | [工具](03_tools/code/)

## 全链路总览

```
          Era 2 流水线                       Era 3 VLA
┌────────────────────────────┐    ┌────────────────────────────┐
│ 视觉感知 → YOLO → 位姿     │    │ 云GPU推理 → 动作序列       │
│    ↓                       │    │    ↓                      │
│  ROS2 Topic → MoveIt2      │    │  WebSocket → Panda执行    │
│    ↓                       │    │    ↓                      │
│  Panda执行 + 状态反馈      │    │  Panda执行 + 四级兜底     │
└────────────────────────────┘    └────────────────────────────┘
```

## 目录结构

```
B_hands_on/
├── README.md                     ← 本文件（入口 + 全链路I/O总览）
├── 01_era2_pipeline/             ← Era 2 流水线
│   ├── io_01_vision.md           ←  视觉感知I/O说明（待补）
│   ├── io_02_yolo_pose.md        ←  YOLO检测+位姿估计（待补）
│   ├── io_03_ros_topic.md        ←  ROS2通信协议（待补）
│   ├── io_04_moveit_plan.md      ←  MoveIt2运动规划（待补）
│   ├── io_05_execute.md          ←  执行+状态反馈（待补）
│   └── code/                     ←  代码：FK/IK/Panda/MoveIt流水线 ✅
│       ├── agibot_demo.py
│       ├── fk_ik_simulator.py
│       ├── interactive_pipeline.py
│       ├── panda_move.py
│       ├── two_link_arm_sim.html
│       └── visual_pipeline.py
├── 02_era3_vla/                  ← Era 3 VLA 模拟
│   ├── io_06_vla_infer.md        ←  云端VLA推理I/O（待补）
│   ├── io_07_fallback.md         ←  四级兜底逻辑（待补）
│   └── code/                     ←  代码：VLA推理/数据飞轮/RL ✅
│       ├── vla_inference_demo.py
│       ├── vla_inference_lite.py
│       ├── vla_pipeline_sim.py
│       ├── data_flywheel_sim.py
│       ├── rl_baseline_demo.py
│       ├── rl_demo_result.png
│       └── cloud_bridge/         ←  云GPU桥接
│           ├── vla_cloud_bridge.py
│           ├── simulate_vla.py
│           ├── panda_executor.py
│           ├── deploy_to_autodl.md
│           └── README.md
├── 03_tools/                     ← 工具说明
│   ├── roi_calculator.md         ←  ROI计算器说明（待补）
│   ├── hand_eye_calib.md         ←  手眼标定说明（待补）
│   ├── failure_diag.md           ←  故障诊断说明（待补）
│   └── code/                     ←  代码：ROI/标定/检查器 ✅
│       ├── roi_calculator.py
│       ├── hand_eye_calibration_sim.py
│       ├── integration_checker.py
│       ├── scenario_visualizer.py
│       └── vla_failure_diagnoser.py
├── 04_simulation/                ← 仿真参考资料 ✅
│   ├── genie_sim_study_guide.md
│   ├── isaac_sim_notes.md
│   └── Genie Sim User Guide.html
└── 05_reference_code/            ← 关键代码片段精讲（待补）
    └── omniagent_excerpts.md
```

## 进度

| 模块 | 状态 | 说明 |
|:---|---:|:---|
| 01_era2 代码 | ✅ Round 1 | FK/IK/MoveIt/Panda 仿真流水线代码就绪 |
| 02_era3 VLA 代码 | ✅ Round 1 | VLA推理/数据飞轮/RL/云桥接代码就绪 |
| 03_tools 代码 | ✅ Round 1 | ROI计算/手眼标定/故障诊断/场景可视化代码就绪 |
| 04_simulation 参考资料 | ✅ Round 1 | Genie Sim精读+Isaac笔记 |
| 01-03 I/O 说明文档 | ⬜ Round 2 | 各环节输入输出文档，需对照 code/ 写 |
| 05 源码精讲 | ⬜ Round 2 | OmniAgent等源码分析 |
