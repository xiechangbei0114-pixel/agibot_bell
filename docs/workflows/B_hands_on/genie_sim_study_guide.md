# 🎮 Genie Sim 源码精读 · 方案岗指南

> 从智元 AIMA 架构的 Genie Sim 源码（76,000 行）中精选方案岗必看的 ~1,500 行。
> 最后更新：2026-06-30 | 面试价值：⭐⭐⭐（面试素材引用）

---

## 一、AIMA 定位

```
AIMA 四大支柱
├── 灵渠 Link-U OS     ← 操作系统（计划 2026 开源 1.0）
├── 灵心 LinkSoul      ← 交互智能体平台
├── 灵创 LinkCraft     ← 内容创作平台
└── 精灵 Genie Studio  ← 仿真引擎 → genie_sim ✅ 已开源
```

---

## 二、阅读路径（由浅入深）

### Step 1: 课程路径（知道 Genie Sim 能干什么）

| 阶段 | 说明 | 面试价值 |
|:---|---:|:---:|
| Stage 0 | 启动 Isaac Sim + 键盘遥控 | 了解 G2 操作方法 |
| Stage 1 | VLN 训练数据采集 | 数据怎么来的 |
| Stage 2 | StreamVLN LoRA 微调 | 模型怎么训练的 |
| Stage 3 | Genie Sim 实时推理 | 模型怎么用的 |

### Step 2: 方案岗必看的 5 份核心源码

| # | 文件 | 大小 | 方案岗价值 |
|:---:|:---|---:|:---|
| 1 | **api_core.py** | 45KB | Genie Sim 中央 API，封装了场景管理、机器人控制、ROS 通信三大块 |
| 2 | **task_benchmark.py** | 16KB | `observe() → policy.predict() → env.step()` 评测循环 |
| 3 | **omniagent.py** | 47KB | **四级兜底的代码实现**——LLM 分解→原子动作→retry回滚 |
| 4 | **llm_scene_generator.py** | 4KB | 自然语言→仿真场景（有限的 DSL + 资产库）|
| 5 | **base.py / pipolicy.py** | — | 策略抽象层，Pi0.5/GR00T 同一接口 |

### Step 3: 策略接口与环境封装

| 文件 | 说明 |
|:---|---:|
| `base.py` | Policy 基类，定义 observe/predict/step 接口 |
| `demopolicy.py` | 人类示教回放（DemoPolicy）|
| `pipolicy.py` | 模型推理策略（PIPolicy）|
| `base_env.py` | 环境基类 |
| `demo_env.py` | 人类示教环境（17KB）|
| `pi_env.py` | 模型推理环境 |

### Step 4: 评测任务配置

| 文件 | 场景 |
|:---|---:|
| `home_g2.json` | 家庭场景 |
| `kitchen_00_g2.json` | 厨房场景 |
| `table_task_g2.json` | 桌面任务 |
| `study_room_00_g2.json` | 书房场景 |

> 结构都是 `task + scene + robot + success_criteria` 四个字段。

---

## 三、面试话术素材

> **"Genie Sim 是智元 AIMA 架构中精灵 Genie Studio 的仿真引擎，通过 APICore 统一暴露场景管理、机器人控制和 ROS 通信三大接口。"**
> → 来自 `api_core.py`

> **"它的 benchmark 框架采用 observe→predict→step 循环，支持 DemoEnv 和 PIEnv 两种评测模式，覆盖 200+ 任务。"**
> → 来自 `task_benchmark.py`

> **"数据采集流水线通过 OmniAgent 做任务编排，LLM 分解任务为原子动作序列，每步有 retry 机制。"**
> → 来自 `omniagent.py`

> **"策略层做了抽象设计，无论跑 Pi0.5 还是 GR00T，接口都是统一的。"**
> → 来自 `base.py`

---

## 四、不需要看的（~74,500 行）

| 跳过 | 原因 |
|:---|---:|
| `benchmark/tasks/` 各任务实现 | 具体逻辑，方案岗不需要 |
| `data_collection/server/` gRPC 服务 | 分布式采集的后端实现 |
| `plugins/` 录制系统 | 技术细节 |
| `utils/` | 通用工具函数 |
| `geniesim/teleop/` | VR 遥操作，不需要 VR 硬件 |
| `scene_reconstruction/` | 3DGS 重建，跟方向无关 |

---

## 📎 关联资料

| 资料 | 位置 |
|:---|---:|
| 源码精读（含课程文件） | `genie_sim_study/`（旧目录，已归档）|
| Isaac Sim 实操笔记 | `isaac_sim_notes.md` |
| Genie Sim 用户手册 | `Genie Sim User Guide.html` |
| 实操流水线总览 | `INDEX.md` |
