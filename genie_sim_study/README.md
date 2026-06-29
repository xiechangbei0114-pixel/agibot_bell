# Genie Sim 3.0 — 方案岗精读指南

> 从智元 AIMA 架构的 Genie Sim 源码中，精选出方案岗真正需要看的核心文件。
> 总代码量 76,000 行中，你只需看 ~1,500 行的关键代码 + 5 份文档。

---

## 阅读顺序（由浅入深）

### Step 1: 先理解架构全貌

| 文件 | 行数 | 价值 |
|------|------|------|
| 项目根目录 `genie_sim_architecture.md` | — | AIMA 定位、"一体三智"映射、模块总览 |

### Step 2: 再看课程路径（知道 Genie Sim 能干什么）

| 文件 | 行数 | 说明 |
|------|------|------|
| `1_course_curriculum/stage0.md` | 148 | 启动 Isaac Sim + 键盘遥控 |
| `1_course_curriculum/stage1.md` | 250 | VLN 训练数据采集 |
| `1_course_curriculum/stage2.md` | 375 | StreamVLN LoRA 微调 |
| `1_course_curriculum/stage3.md` | 212 | GenieSim 实时推理 |

> 不需要实操，快速浏览了解"数据采集→训练→推理"的闭环即可。

### Step 3: 精读源码 — 方案岗必看的 5 份文件

按重要程度排序：

#### 1. `2_key_source_code/api_core.py` (45KB)

**Genie Sim 的中央 API，所有能力的统一入口。**

- 单例模式，封装了场景管理、机器人控制、ROS 通信三大块
- 看 `set_robot_pose()`, `move_to_pose()`, `add_object()`, `get_camera_rgbd()` 这几个核心方法
- **方案岗价值：** 理解 Genie Sim 暴露了哪些能力——方案里说"Genie Sim 支持 X"时，你知道 X 的 API 在哪里

#### 2. `2_key_source_code/task_benchmark.py` (16KB)

**评测框架的主循环。**

- 看 `observe() → policy.predict() → env.step()` 这个循环结构
- 理解 DemoEnv / PIEnv / AbsPoseEnv 三种环境类型的区别
- **方案岗价值：** 理解 benchmark 怎么跑——写方案时引用"200+ 任务 / 100,000+ 场景 / sim-to-real gap < 10%"时，知道数据从哪来的

#### 3. `2_key_source_code/omniagent.py` (47KB)

**自动化数据采集的编排核心——你"四级兜底"方案的代码实现。**

- 看 LLM 任务分解 → Layout Generator → 原子动作执行 → 错误恢复 这条线
- 重点看 `execute_task()` 和错误处理逻辑
- **方案岗价值：** 面试时能说"我看了 OmniAgent 的源码，它把任务分解为 approach→grasp→place→insert 原子动作，每步都有 retry 机制"

#### 4. `2_key_source_code/llm_scene_generator.py` (4KB)

**自然语言→仿真场景。**

- 用户说"在厨房放一个杯子和一个盘子"，它就生成 USD 场景
- **方案岗价值：** 理解"LLM 驱动的场景泛化"不是黑魔法，是有限的 DSL + 资产库

#### 5. `2_key_source_code/app_main_loop.py` (3.2KB)

**仿真主循环——physics + render 的调度。**

- **方案岗价值：** 知道仿真引擎的主循环结构就够了

### Step 4: 看策略接口（理解 Policy 抽象层）

| 文件 | 说明 |
|------|------|
| `2_key_source_code/base.py` | Policy 基类，定义 `observe()`, `predict()`, `step()` 接口 |
| `2_key_source_code/demopolicy.py` | 人类示教回放（DemoPolicy） |
| `2_key_source_code/pipolicy.py` | 模型推理策略（PIPolicy） |

> **方案岗价值：** 理解"策略抽象层"设计——无论后面跑 Pi0.5 还是 GR00T，接口不变。

### Step 5: 看环境封装（理解评测怎么组织）

| 文件 | 说明 |
|------|------|
| `2_key_source_code/base_env.py` (7KB) | 环境基类 |
| `2_key_source_code/demo_env.py` (17KB) | 人类示教环境 |
| `2_key_source_code/pi_env.py` (6KB) | 模型推理环境 |

### Step 6: 看评测任务配置（理解"200+ 任务"长什么样）

| 文件 | 说明 |
|------|------|
| `4_sample_task_configs/home_g2.json` | 家庭场景 |
| `4_sample_task_configs/kitchen_00_g2.json` | 厨房场景 |
| `4_sample_task_configs/table_task_g2.json` | 桌面任务 |
| `4_sample_task_configs/study_room_00_g2.json` | 书房场景 |

> 随便打开一个 JSON 看看结构：`task`, `scene`, `robot`, `success_criteria` 四个字段。

---

## 面试话术素材

以下话术来自这些源码，可直接用在面试中：

> **"Genie Sim 是智元 AIMA 架构中精灵 Genie Studio 的仿真引擎，通过 APICore 统一暴露场景管理、机器人控制和 ROS 通信三大接口。"**
> → 来自 `api_core.py` 的架构设计

> **"它的 benchmark 框架采用 observe→predict→step 循环，支持 DemoEnv 和 PIEnv 两种评测模式，覆盖 200+ 任务。"**
> → 来自 `task_benchmark.py` + `benchmark/envs/`

> **"数据采集流水线通过 OmniAgent 做任务编排，LLM 分解任务为原子动作序列，每步有 retry 机制。"**
> → 来自 `omniagent.py`

> **"策略层做了抽象设计，无论跑 Pi0.5 还是 GR00T，接口都是统一的。"**
> → 来自 `benchmark/policy/base.py`

---

## 不需要看的（76,000 行中 ~74,500 行）

| 跳过内容 | 原因 |
|----------|------|
| `benchmark/tasks/` 各任务实现 | 200 个任务各自的具体逻辑，方案岗不需要 |
| `data_collection/server/` gRPC 服务 | 分布式采集的后端实现 |
| `plugins/` 录制系统 | 技术细节 |
| `utils/` | 通用工具函数 |
| `geniesim/teleop/` | VR 遥操作，你不需要 VR 硬件 |
| `scene_reconstruction/` | 3DGS 重建，跟你的方向无关 |

---

## 资料来源

- 代码提取自 `03_lightweight_pack/lightweight_pack/genie_sim/source/`
- 课程文件来自 `01_AIMA_genie_sim_code/genie_sim/stage*.md`
- 原始仓库: https://github.com/AgibotTech/genie_sim (MPL 2.0)
