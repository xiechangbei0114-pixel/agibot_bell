# 🔧 实操流水线 · B_hands_on

> 入口 | [Era 2 流水线](01_era2_pipeline/) | [Era 3 VLA](02_era3_vla/) | [仿真参考](04_simulation/)

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
├── 01_era2_pipeline/             ← Era 2 各环节输入输出说明
│   ├── io_01_vision.md           ←  视觉感知：输入→处理→输出
│   ├── io_02_yolo_pose.md        ←  YOLO检测+位姿估计
│   ├── io_03_ros_topic.md        ←  ROS2通信协议
│   ├── io_04_moveit_plan.md      ←  MoveIt2运动规划
│   └── io_05_execute.md          ←  执行+状态反馈
├── 02_era3_vla/                  ← Era 3 VLA 模拟
│   ├── io_06_vla_infer.md        ←  云端VLA推理I/O
│   └── io_07_fallback.md         ←  四级兜底逻辑
├── 03_tools/                     ← 工具说明
│   ├── roi_calculator.md
│   ├── hand_eye_calib.md
│   └── failure_diag.md
├── 04_simulation/                ← 仿真参考资料
│   ├── genie_sim_study_guide.md
│   ├── isaac_sim_notes.md
│   └── Genie Sim User Guide.html
└── 05_reference_code/            ← 关键代码片段精讲（待补）
    └── omniagent_excerpts.md
```

## 进度

| 模块 | 状态 | 说明 |
|:---|---:|:---|
| 04_simulation 参考资料 | ✅ Round 1 | Genie Sim精读+Isaac笔记 |
| 01_era2 I/O 说明 | ⬜ Round 2 | 各环节输入输出文档 |
| 02_era3 VLA I/O 说明 | ⬜ Round 2 | VLA推理+兜底逻辑 |
| 03_tools 工具说明 | ⬜ Round 2 | ROI/标定/诊断 |
| 05 源码精讲 | ⬜ Round 2 | OmniAgent等源码分析 |
