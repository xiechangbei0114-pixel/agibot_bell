# 🗺️ 具身智能实战路线图 · 完整版

> 最后更新: 2026-06-22 | 硬件: GTX 1060 6GB | 目标: 智元方案岗

---

## 📍 你当前的位置

```
           你现在在这里
               │
               ▼
   Week 1           Week 2            Week 3-8
  ROS2+Panda       VLA技术栈          方案输出+面试
  ✅ 已完成        🟡 调研中          ⬜
```

### 已具备的能力

| 能力 | 证据 | 面试价值 |
|:---|:---|:---:|
| 工业产线经验 3 年 | 歌尔 | ⭐⭐⭐⭐⭐ |
| 工业视觉（YOLO / SuperPoints） | 歌尔落地 | ⭐⭐⭐⭐⭐ |
| ROS2 + Topic 通信 | `agibot_demo.py` 跑通 | ⭐⭐⭐⭐ |
| Panda + MoveIt2 控制 | `panda_move.py` 跑通 | ⭐⭐⭐⭐ |
| VLA 概念（大小脑 / Action CoT） | 已学 | ⭐⭐⭐⭐ |
| 四级兜底设计 | 方案已写 | ⭐⭐⭐⭐⭐ |
| Agent 产品 0→1 | 工作流兜底 | ⭐⭐⭐⭐ |
| PMP | 已考 | ⭐⭐⭐ |
| **上下料方案框架** | `solution_loading_unloading.md` | ⭐⭐⭐⭐⭐ |

---

## 🧠 2026年最新 VLA 模型全景（可直接用的）

以下 4 个方案，从最容易到最难，你可选一个执行：

### 方案 A：GR00T N1.7（NVIDIA · 2026年4月发布⭐⭐⭐）

| 项目 | 内容 |
|:---|:---|
| **链接** | [github.com/NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) |
| **许可** | Apache 2.0（商用友好） |
| **参数** | 3B（轻量） |
| **硬件** | 推理 16GB+ VRAM / 微调 40GB+ |
| **特点** | ✅ 开源 ✅ 跨 32 种机器人 ✅ 有人类视频预训练 |
| **你的方案岗价值** | ⭐⭐⭐⭐⭐ 面试直接提「我看过 GR00T N1.7 源码」 |
| **能跑吗？** | ❌ GTX 1060 不行 → 需租 AutoDL RTX 4090 |

**快速体验（不需要 GPU）：**
```bash
# 在你的 WSL Ubuntu 里就能跑 open-loop 推理
# 不需要 GPU！只是拿 demo 数据跑一遍，看 GR00T 的输入输出格式
git clone --recurse-submodules https://github.com/NVIDIA/Isaac-GR00T.git
cd Isaac-GR00T
uv sync --python 3.10
# 运行 open-loop 推理（CPU only，看结果）
uv run python scripts/deployment/standalone_inference_script.py \
  --model-path nvidia/GR00T-N1.7-3B \
  --dataset-path demo_data/droid_sample \
  --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT \
  --traj-ids 1 2 \
  --inference-mode pytorch \
  --action-horizon 8
```

### 方案 B：Pi0.5（Physical Intelligence · 2025年9月）

| 项目 | 内容 |
|:---|:---|
| **链接** | [github.com/Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) |
| **许可** | Apache 2.0 |
| **硬件** | 推理 8GB+ VRAM / 微调 22.5GB+ |
| **特点** | ✅ 开源 ✅ Knowledge Insulation ✅ SOTA |
| **你的方案岗价值** | ⭐⭐⭐⭐⭐ Genie Sim 3.0 的 benchmark 对比就是基于 Pi0.5 |
| **能跑吗？** | ❌ GTX 1060 6GB 差一点 → AutoDL 最低 ¥2/h |

**快速体验（不需要 GPU）：**
```bash
git clone --recurse-submodules https://github.com/Physical-Intelligence/openpi.git
cd openpi
GIT_LFS_SKIP_SMUDGE=1 uv sync
# 看代码结构、看它怎么定义输入输出
less src/openpi/policies/libero_policy.py
```

### 方案 C：ACoT-VLA（智元 · CVPR 2026 ⭐⭐⭐）

| 项目 | 内容 |
|:---|:---|
| **链接** | [github.com/AgibotTech/ACoT-VLA](https://github.com/AgibotTech/ACoT-VLA) |
| **论文** | [arxiv.org/abs/2601.11404](https://arxiv.org/abs/2601.11404) |
| **特点** | ✅ **智元自己出的模型** ✅ CVPR 2026 ✅ Action CoT |
| **你的方案岗价值** | ⭐⭐⭐⭐⭐ **面试必提！「我看过智元 ACoT-VLA 的论文和代码」** |
| **能跑吗？** | ❌ 同 Pi0.5 需要 GPU |

### 方案 D：Genie Sim 3.1（智元 · 2026年4月）

| 项目 | 内容 |
|:---|:---|
| **链接** | [github.com/AgibotTech/genie_sim](https://github.com/AgibotTech/genie_sim) |
| **硬件** | 最低 RTX 4080 / 32GB RAM |
| **版本** | v3.1（支持 Genie Sim World、RLinF、G2 机器人全身控制） |
| **你的方案岗价值** | ⭐⭐⭐⭐⭐ **必须了解，可以看文档不看代码** |

**你能做的（不需要 GPU）：**
```bash
# 1. 看你已下载的 Genie Sim User Guide.html
# 2. 看 GitHub README，了解它能干什么
# 3. 了解 benchmark leaderboard 上的数据
```

---

## 🎯 核心实操清单（按优先级排序）

### 🔴 P0：必须做（2-3 天）

| # | 实操 | 做什么 | 面试价值 |
|:---:|:---|:---|:---:|
| 1 | **看 GR00T N1.7 源码结构** | clone repo，理解它的输入输出格式、embodiment tag 概念 | 证明你懂 VLA 的工程实现 |
| 2 | **看 Genie Sim 3.1 文档** | 看你已下载的 HTML，了解场景生成、benchmark、leaderboard | 证明你了解智元平台 |
| 3 | **完善方案 PPT** | 把 `solution_loading_unloading.md` 转成 PPT | **敲门砖** |

### 🟡 P1：建议做（1-2 天）

| # | 实操 | 做什么 | 方法 |
|:---:|:---|:---|:---|
| 4 | **AutoDL 租 GPU 跑推理** | 最低 ¥2/h 租 RTX 3090 | 部署 Pi0.5 或 GR00T 推理 |
| 5 | **云端→本地桥接** | 用我写的 `vla_cloud_bridge.py` | 云端推 → WSL Panda 执行 |
| 6 | **本地模拟 VLA Demo** | 用 `simulate_vla.py` + `panda_executor.py` | 不需要 GPU，跑通整个链路 |

### 🟢 P2：有时间做

| # | 实操 | 做什么 | 时间 |
|:---:|:---|:---|:---|
| 7 | Generator Sim 云端体验 | 注册 Genie Sim 云端 | 1h |
| 8 | 6D 位姿 + 手眼标定 | 搜 PnP 和标定流程 | 1h |
| 9 | 力控概念 | 搜阻抗/导纳控制 | 1h |

---

## 📅 7 天冲刺计划

| 天 | 做什么 | 产出 |
|:---:|:---|:---|
| **今天** | ① 读完这个路线图 ② clone GR00T + OpenPI 源码 ③ 开始看 Genie Sim 文档 | 理解 VLA 模型的全貌 |
| **Day 2** | ① 完善方案 PPT ② 在 WSL 跑通 `simulate_vla.py` + `panda_executor.py` Demo | **可展示的 Demo** |
| **Day 3** | ① 注册 AutoDL ② 部署 GR00T N1.7 或 Pi0.5 推理 ③ 跑通云端→本地桥接 | **端到端链路** |
| **Day 4** | ① 看 ACoT-VLA 论文 + 源码 ② 补 6D 位姿/手眼标定 | 知识补齐 |
| **Day 5** | ① 完善方案 PPT v2 ② 加入 Genie Sim 和 GR00T 的调研结论 | 方案加深 |
| **Day 6** | ① 准备面试 12 题话术 ② 练习 3 分钟方案讲解 | 面试准备 |
| **Day 7** | ① 简历用具身语言重构 ② 附方案作品集 ③ **投递** | **敲门砖** |

---

## 🔧 实操详细步骤

### Step 1：克隆最新 VLA 源码（今天就能做）

```bash
# 在你的 WSL Ubuntu 里（不需要 GPU）

# 1. GR00T N1.7（NVIDIA 最新）
git clone --recurse-submodules https://github.com/NVIDIA/Isaac-GR00T.git

# 2. OpenPI（Pi0/Pi0.5 官方）
git clone --recurse-submodules https://github.com/Physical-Intelligence/openpi.git

# 3. ACoT-VLA（智元，CVPR 2026）
git clone --recurse-submodules https://github.com/AgibotTech/ACoT-VLA.git

# 4. Genie Sim（智元仿真平台）
git clone https://github.com/AgibotTech/genie_sim.git
```

然后花 30 分钟看每个 repo 的结构，理解：
- 输入是什么格式（图像 + 指令 + 状态）
- 输出是什么格式（action chunk）
- 怎么定义 embodiment（机器人配置）
- 怎么启动推理服务

### Step 2：在 WSL 跑通本地 Demo

```bash
# 已经有 Panda 仿真环境的情况下
# 参考 cloud_vla_bridge/ 下的文件

# 终端 1: Panda 仿真
ros2 launch panda_moveit_config panda_gazebo.launch.py

# 终端 2: VLA 模拟器（不需要 GPU）
python3 cloud_vla_bridge/simulate_vla.py

# 终端 3: 执行器
python3 cloud_vla_bridge/panda_executor.py

# 终端 4: 触发来料
ros2 topic pub /parts_detected std_msgs/msg/String "data: '1|CPU芯片|0.02|-0.01'"
```

### Step 3：租 AutoDL 跑真实 VLA 推理

```
1. 打开 autodl.com 注册
2. 选择 GPU: RTX 4090 (~¥4/h) 或 RTX 3090 (~¥2/h)
3. 选择镜像: PyTorch 2.x + CUDA 12.x
4. 开机后 SSH 连接
5. 克隆 GR00T 或 OpenPI
6. 运行推理
7. 用 vla_cloud_bridge.py 连接云端→本地
```

### Step 4：看 Genie Sim 文档（已下载）

你已经有 `Genie Sim User Guide.html`，重点看：
- 3.1 Benchmark Evaluation（了解 benchmark 怎么跑）
- 3.2 Scene Generator（LLM 驱动场景生成）
- Leaderboard 数据（Pi0.5 vs GR00T vs ACoT 的对比）

---

## 💡 面试必杀技：你比其他人强在哪

### 你的 3 个缝合故事

```
缝合 1: "我做 Agent 产品时 LLM + 工作流兜底
         → 跟 VLA + 四级兜底是同一个架构逻辑"
         （证明你的 Agent 经验可迁移）

缝合 2: "我在歌尔做工业视觉 3 年
         → VLA 失败后的第二层兜底就是我的老本行"
         （证明你有别人没有的工业经验）

缝合 3: "我做过越南跨国交付
         → 产线方案落地不只是技术问题，是项目管理问题"
         （证明你有全局视野）
```

### 面试 30 秒自我介绍

> "我有 3 年工业产线经验，做过工业视觉落地和 Agent 产品 0 到 1。我的核心能力是**把 VLA 的泛化能力和工业级的可靠性结合起来**——VLA 做主力泛化抓取，传统视觉做精确纠偏，力控做物理兜底。我看过 GR00T N1.7 的源码和 Genie Sim 3.1 的文档，也跑通了云端推理到本地执行的端到端 Demo。"

---

## 📚 资料索引（一键直达）

| 资料 | 链接 | 优先级 |
|:---|:---|:---:|
| GR00T N1.7 源码 | [GitHub](https://github.com/NVIDIA/Isaac-GR00T) | 🔴 |
| GR00T N1.7 论文 | [arXiv](https://arxiv.org/abs/2503.14734) | 🔴 |
| Pi0.5 源码 | [GitHub](https://github.com/Physical-Intelligence/openpi) | 🔴 |
| ACoT-VLA 智元模型 | [GitHub](https://github.com/AgibotTech/ACoT-VLA) | 🔴 |
| ACoT-VLA 论文 | [arXiv](https://arxiv.org/abs/2601.11404) | 🔴 |
| Genie Sim 3.1 | [GitHub](https://github.com/AgibotTech/genie_sim) | 🔴 |
| Genie Sim 文档 | 已下载的 HTML | 🔴 |
| OpenVLA | [GitHub](https://github.com/openvla/openvla) | 🟡 |
| 智元 AIMA 平台 | Genie Sim 文档 | 🟡 |
| AutoDL 云 GPU | [autodl.com](https://www.autodl.com) | 🟡 |
