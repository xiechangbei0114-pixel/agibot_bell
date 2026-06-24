# AGIBOT · 具身智能方案岗实战

> 目标: 智元方案岗 | 硬件: GTX 1060 6GB | 启动: 2026.06.17

---

## 📂 项目结构

```
AGIBOT/
│
├── README.md                       # ← 你现在看的
├── todo.md                         # 任务清单 (每日更新)
├── 8week_plan_embodied_ai.md       # 8周学习计划 (主计划)
├── MASTER_ROADMAP.md               # 完整路线图 (补充参考)
│
├── docs/                           # 📚 文档中心
│   ├── solutions/                  #    敲门砖方案
│   │   └── solution_loading_unloading.md
│   └── reference/                  #    参考资料
│       ├── Genie Sim User Guide.html
│       ├── high_roi_embodied_ai_scenarios.md
│       ├── agibot_feasibility.md
│       └── resume.md
│
├── src/                            # 💻 自己写的代码
│   ├── week_1/                     #    ROS2 + Panda 控制
│   │   ├── agibot_demo.py          #    产线Topic通信
│   │   ├── panda_move.py           #    Panda MoveIt2控制
│   │   ├── fk_ik_simulator.py      #    FK/IK仿真
│   │   └── two_link_arm_sim.html   #    二连杆可视化
│   ├── week_2/                     #    VLA仿真 + 工具
│   │   ├── vla_pipeline_sim.py     #    VLA流水线量化对比
│   │   ├── data_flywheel_sim.py    #    冷启动数据飞轮
│   │   ├── era3_vla_demo.py        #    Era 3 VLA端到端(numpy)
│   │   └── era3_vla_demo_lite.py   #    Era 3 VLA端到端(纯Python)
│   ├── week_3/                     #    VLA翻车诊断
│   │   └── vla_failure_diag.py
│   ├── week_4/
│   │   └── roi_calculator.py       #    ROI计算器
│   ├── week_5/
│   │   └── scenario_visualizer.py  #    场景可视化
│   ├── week_6/
│   │   └── integration_checker.py  #    整合检查
│   └── cloud_vla_bridge/           #    ☁️ 云端VLA→本地Panda
│       ├── simulate_vla.py         #    VLA推理模拟器
│       ├── panda_executor.py       #    机械臂执行器(+兜底)
│       ├── vla_cloud_bridge.py     #    云端桥接(WebSocket)
│       └── deploy_to_autodl.md     #    云端部署指南
│
├── third_party/                    # 📦 第三方VLA源码(已克隆)
│   ├── gr00t/                      #    NVIDIA GR00T N1.7
│   ├── openpi/                     #    Pi0/Pi0.5
│   ├── acot_vla/                   #    智元ACoT-VLA
│   └── genie_sim/                  #    智元Genie Sim
│
├── journal/                        # 📝 个人日志
│   └── journal.md
│
└── .vscode/                        # ⚙️ VS Code配置
    └── settings.json
```

## 🔗 核心架构

```
Windows (你的老本行)                       WSL (ROS2)
─────────────────────                     ────────────
YOLO / OpenCV                            Panda MoveIt2
     │                                        │
     └── ROS2 Topic ──────────────────────────▶
         /parts_detected                      Gazebo仿真
         /vla_pose
         /mes_report
         /vla_inference_log
```

## 🎯 8周总目标

```
Wk1-2 理论打底 → Wk3 实操冲刺 → Wk4-5 方案输出 → Wk6-7 打磨面试 → Wk8 投递
06.17-06.30      07.01-07.07     07.08-07.21     07.22-08.04    08.05-08.11
✅ 95%           ⬜              ⬜               ⬜             ⬜
```

## 📊 当前进度 (2026-06-24)

| 领域 | 进度 | 说明 |
|:---|:---:|:---|
| 理论12概念 | ✅ 95% | 知识自检已补完 |
| WSL+ROS2环境 | ✅ 就绪 | Gazebo + MoveIt2 可跑 |
| Era 3 VLA仿真 | ✅ 已创建 | era3_vla_demo.py / era3_vla_demo_lite.py |
| 模拟VLA→Panda | 📝 待跑通 | simulate_vla.py + panda_executor.py |
| Era 2视觉流水线 | 📝 待做 | Window图→YOLO→Topic→WSL |
| 方案PPT | 📝 Week4-5 | solution_loading_unloading.md 已就绪 |

> 完整学习计划 → `MASTER_ROADMAP.md`
> 每日任务 → `todo.md`
