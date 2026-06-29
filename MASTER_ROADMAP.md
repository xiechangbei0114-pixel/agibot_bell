# 🗺️ 具身智能实战路线图

> 最后更新: 2026-06-29 | 目标: **智元方案岗**
> 硬件: GTX 1060 6GB | WSL2+ROS2: ✅ 就绪 | 公司有智元真机
> 状态: Wk1-2 ✅ | Wk3 🟡 理论通 | Wk4 ✅ 方案初版 | 🎯 面试策略: 先练手2-3家 → 再面智元

---

## 📍 当前位置

```
08周总目标: 一套方案(PDF) + 一套话术(脱稿) + 简历投出去

06.17             07.01           07.08           07.22           08.05
 │                 │               │               │               │
 Wk1-2            Wk3              Wk4-5           Wk6-7           Wk8
理论打底         翻车+实操        方案输出        实战面试        投递冲刺
──────▶           +话术打磨       +练手面2-3家   目标面智元
✅ 完成           🟡 理论通        🟢 方案初版      🎯              ⬜

### 你与 985 应届生的核心差异

```
你有但对方没有:                         对方有你没有:
✅ 歌尔 3 年产线经验 (懂客户要什么)         ❌ 985 学历
✅ 工业视觉落地 (YOLO/SuperPoints)         ❌ 论文发表
✅ Agent 产品 0→1 (兜底架构思想相同)        ❌ 能调模型
✅ PMP + 跨国交付
✅ 公司有智元真机

→ 方案岗看的是「能否解决产线问题」，不是学校。
  你的经验优势足够弥补学历差距。重点是把经验用「具身智能术语」翻译一遍。
```

---

## 📅 8 周计划

| 阶段 | 时间 | 核心目标 | 状态 |
|:---:|:---:|:---|:---:|
| **① 理论打底** | 06.17-06.30 | 12核心概念掌握 + Day14考核 | 🟡 95%完成，话术待练 |
| **② 翻车+实操** | 07.01-07.07 | VLA翻车模式 + 3个实操跑通 | ⬜ |
| **③ 方案输出** | 07.08-07.21 | 三场景方案 + PPT | ⬜ |
| **④ 打磨+面试** | 07.22-08.04 | 话术脱稿 + 简历重构 + 模拟面试 | ⬜ |
| **⑤ 投递** | 08.05-08.11 | 投智元 + Figure + 星动纪元 | ⬜ |

### Week 1-2 (已完成) ✅ 产出清单

| 分类 | 具体内容 |
|:---|:---|
| 🧠 理论 (12概念95%) | 机器人分类、四层架构、ROS3通信+AimRT、FK/IK、VLA大小脑、三大模型对比、仿真栈、RLvsIL、Sim2Real、冷启动三阶段、兜底金字塔、范式四阶段演进 |
| 💻 代码 | `agibot_demo.py` `panda_move.py` `fk_ik_simulator.py` `simulate_vla.py` `panda_executor.py` `vla_cloud_bridge.py` `era3_vla_demo.py` |
| 📦 资产 | 源码克隆 (genie_sim / openpi / ACoT-VLA / Genie-Envisioner)、方案框架、云端桥接、代码分析 |
| 🏛️ AIMA 开源全景 | ✅ 下详「AIMA 架构与智元开源全景」 |
| 🔧 环境 | WSL + ROS2 Humble + MoveIt2 + Gazebo 已就绪 |

### Week 3 (07.01-07.07) 🔜 翻车+实操冲刺

**实操任务（已在云GPU上完成）：**
| # | 实操 | 状态 |
|:---:|:---|:---:|
| 0 | Isaac Sim 启动+加载场景+遥控移动 | ✅ AIMA Genie Sim |
| 1 | **OpenPI 推理 + Genie Sim 显示** | ✅ VLA全链路跑通 |
| 2 | Genie Sim 源码76,000行精读 | ✅ 方案岗必看1,500行 |
| 天 | 主题 | 场景关联 |
|:---:|:---|:---|
| 15 | VLA 翻车模式清单 (5大类) | A新物体/B高精度/C光照 |
| 16 | VLA vs 确定性选择标准 | 三场景决策树 |
| 17 | 根因分析框架 | 三场景排查路径不同 |
| 18 | 🔧 去公司看智元机器人 | 现场笔记 |
| 19 | 竞品深度对比 | Amazon/Figure/Lely |
| 20 | 300字缝合话术 | 三版本 |
| 21 | 每周复盘 | |

**3 个实操任务（本周核心）：**
| # | 实操 | 说明 |
|:---:|:---|:---|
| 1 | **Era 2 视觉抓取流水线** | Windows图→YOLO→ROS2→WSL→MoveIt2 |
| 2 | **Era 3 模拟VLA推理** | simulate_vla + panda_executor 跑通 |
| 3 | **四级兜底Demo** | VLA失败→视觉重试→力控→报警 |

### Week 4-5 (07.08-07.21) 📄 方案输出 + 话术打磨

| 周 | 任务 | 产出 |
|:---:|:---|:---|
| 4 | 三大场景深度方案 (仓储/制造/农业) | 三份产品简报 |
| 4 | **12题话术逐题录音** (每天3题) | 每题3分钟脱稿 |
| 5 | PPT制作 (10页主方案+3页附录) | 模块化PPT |
| 5 | **练手面试准备** | 投宇树/星动纪元 |

### Week 6-7 (07.22-08.04) 🗣️ 实战面试

| 周 | 任务 | 目标公司 |
|:---:|:---|:---|
| 6 | 🔵 **练手面**（2-3家） | 宇树 → 星动纪元 → 银河通用 |
| 6 | 每面完复盘，完善话术 | 查漏补缺 |
| 7 | 🟢 **目标面** | **智元** 🎯 + Figure + 1X |
| 7 | 简历重构 + 3个缝合故事 + 模拟面试 | 拿到至少1个offer保底 |

### Week 8 (08.05-08.11) 🚀 投递

| 批次 | 公司 | 说明 |
|:---:|:---|:---|
| 🔵 练手 | **宇树** | 方案岗，人形机器人认知要求 |
| 🔵 练手 | **星动纪元** | 清华系，偏学术，会问得细 |
| 🔵 练手 | **银河通用** | 偏商业化落地，场景题多 |
| 🟢 目标 | **智元** 🎯 | 最想去，火力全开 |
| 🟢 目标 | **Figure AI** | 海外人形机器人头部 |
| 🟢 目标 | **1X Technologies** | 挪威，具身智能 |
| 🟡 备选 | **魔法原子 (MagicAtom)** | 国产人形机器人新锐 |
| 🟡 备选 | **傅利叶智能 (Fourier)** | 通用机器人+康复 |
| 🟡 备选 | **逐际动力 (LimX)** | 足式机器人+操作 |

---

## 🏛️ AIMA 架构与智元开源全景（面试第10题素材）

> AIMA = AI Machine Architecture，2026.06.09 发布，四个平台

```
AIMA 四大支柱
├── 灵渠 Link-U OS     ← 操作系统，计划2026开源1.0（尚未发布）
├── 灵心 LinkSoul      ← 交互智能体平台（未开源）
├── 灵创 LinkCraft     ← 内容创作平台（未开源）
└── 精灵 Genie Studio  ← 仿真引擎 → genie_sim ✅ 已开源
```

### 已开源到本地的资产

| 仓库 | 路径 | 大小 | 说明 |
|:---|:---|---:|:---|
| **genie_sim** | `../01_AIMA_genie_sim_code/` | ~2GB | 仿真引擎+场景生成器+StreamVLN |
| **genie_sim 轻量版** | `../02_genie_sim_lightweight/` | ~70MB | 裁剪版，不含资产纹理 |
| **ACoT-VLA** | `../ACoT-VLA/` | 2.9M | CVPR 2026 — Action Chain-of-Thought for VLA |
| **Genie-Envisioner** | `../Genie-Envisioner/` | 52M | 统一世界模型平台，操作推理 |

### 智元其他已开源的仓库（AgibotTech GitHub）

| 仓库 | 方向 | 面试价值 |
|:---|:---|---:|
| `agibot_x1_infer/train/hardware` | X1 人形机器人全套 | ⭐⭐ 了解生态即可 |
| `GO-1 / GO-1 Air` (OpenDriveLab) | ViLLA 架构 VLA 模型 | ⭐⭐⭐⭐⭐ **面试核心** |
| `ACoT-VLA` | VLA + Action Chain-of-Thought | ⭐⭐⭐⭐ 面试加分项 |
| `Genie-Envisioner` | 世界模型 + 操作 | ⭐⭐⭐⭐ Sim2Real 话题 |
| `EWMBench` | 世界模型评测 | ⭐⭐ 了解即可 |

### 面试话术（10-15秒）

> "智元的 AIMA 是行业首个开放的具身智能生态体系，包含灵渠OS、灵心、灵创、精灵四个平台。其中仿真引擎 genie_sim 已开源，VLA 模型 GO-1（基于 ViLLA 架构，IROS 2025 Finalist）也在 GitHub 和 HuggingFace 上可以下载权重。2026年灵渠OS也将开源。"

---

## 🤔 你的 WSL2 能做什么？
|:---|:---:|:---|
| Era 2: Panda 抓取 | ✅ 已能做 | `panda_move.py` |
| Era 2: + 模拟相机 | 🟡 卡但能用 | Gazebo 相机插件 (WSL2无GPU加速) |
| Era 2: + YOLO 检测 | ✅ 能做 | Windows图片→Topic→WSL |
| Era 2: 完整流水线 | ✅ 能做 | 图片→YOLO→位姿→IK→MoveIt2 |
| Era 3: 模拟VLA | ✅ 已写好 | `simulate_vla.py` + `panda_executor.py` |
| Era 3: 真实VLA | ❌ 需AutoDL | ¥2-4/h租RTX 3090/4090 |
| Genie Sim | ❌ 需RTX 4080+ | 硬件不够 |

---

## 🎯 三大杀手级场景（面试核心武器）

> 面试官问场景题时，用这三套框架回答。

| 场景 | 对标企业 | 核心逻辑 | 你的经验缝合 |
|:---|:---|:---|:---|
| **A 仓储物流** 🏭 | Amazon Vulcan, Agility Digit | SKU多精度低→VLA天然优势 | AGV仓储盘点项目 |
| **B 制造业** 🔧 | Figure×BMW, Hyundai | 精度高节拍快→兜底设计关键 | 歌尔3C产线经验 |
| **C 农业/特殊** 🌾 | Lely 奶牛场机器人 | 环境恶劣ROI高→RaaS模式 | 越南交付的破局思维 |

### 场景 → 技能优先级

| 技能 | 场景A | 场景B | 场景C |
|:---|:---:|:---:|:---:|
| VLA大小脑 | ★★★★★ | ★★★★ | ★★★ |
| 兜底设计 | ★★★★★ | ★★★★★ | ★★★★ |
| 冷启动 | ★★★★★ | ★★★★ | ★★ |
| 翻车诊断 | ★★★★★ | ★★★★★ | ★★★ |
| 安全标准 | ★★★ | ★★★★★ | ★★★ |
| 手眼标定 | ★★★★ | ★★★★★ | ★★★ |
| RaaS商业 | ★★★★ | ★★★ | ★★★★★ |

---

## 🏆 面试 12 题自检

| # | 问题 | 你的锚点 | 场景 |
|:---:|:---|:---|:---:|
| 1 | 「做过机械臂吗？」 | MoveIt2 + Python，知VLA边界 | A/B |
| 2 | 「机器人控制是什么？」 | 四代演进：示教器→ROS→VLA→世界模型 | A/B/C |
| 3 | **「仓储物流怎么看？」** | Amazon对标，标准品建基线→非标打溢价 | **A** |
| 4 | **「制造业怎么落地？」** | ISO 10218 + 99.99% + 四级兜底 | **B** |
| 5 | **「农业机会？」** | Lely启示：形态决定功能，RaaS降门槛 | **C** |
| 6 | 「VLA vs 传统怎么选？」 | 泛化vs可靠性trade-off→场景决策树 | A/B |
| 7 | 「冷启动怎么办？」 | 规则→遥操作→飞轮，三场景策略不同 | A |
| 8 | 「人形机器人趋势？」 | 范式演进视角+三场景最适合形态 | A/B/C |
| 9 | 「智元 vs 宇树？」 | 产品+生态差异，智元场景B有优势 | B |
| 10 | 「了解智元吗？」 | AIMA (灵渠/Genie Studio/Genie Sim/GO-2) | A/B |
| 11 | 「经验能迁移吗？」 | 3个缝合故事各对应一个场景 | A/B/C |
| 12 | 「凭什么胜任？」 | 懂工业落地+懂VLA边界+懂兜底+懂三场景 | A/B/C |

---

## 🔧 实操清单 (按优先级)

| # | 实操 | 面试价值 | 状态 |
|:---:|:---|:---:|:---:|
| 1 | ROS2+Panda Python | ⭐⭐⭐⭐ | ✅ |
| 2 | 产线Topic通信Demo | ⭐⭐⭐⭐ | ✅ |
| 3 | Era 3 VLA端到端仿真 | ⭐⭐⭐⭐ | ✅ |
| 4 | **Era 2 视觉抓取流水线** | ⭐⭐⭐⭐⭐ | ⬜ Week3 |
| 5 | **Era 3 模拟VLA+Panda** | ⭐⭐⭐⭐⭐ | ⬜ Week3 |
| 6 | **四级兜底Demo** | ⭐⭐⭐⭐⭐ | ⬜ Week3 |
| 7 | Genie Sim文档调研 | ⭐⭐⭐ | 🟡 |
| 8 | 去公司看智元机器人 | ⭐⭐⭐⭐⭐ | 🟡 |
| 9 | 三场景方案简报 | ⭐⭐⭐⭐⭐ | ⬜ Week4 |
| 10 | 模块化PPT | ⭐⭐⭐⭐⭐ | ⬜ Week5 |
| 11 | 路演录音 | ⭐⭐⭐⭐⭐ | ⬜ Week6 |

---

## 📁 项目结构

```
AGIBOT/                            # E:\0_1493677\11_AGIBOT\agibot_bell\
├── MASTER_ROADMAP.md              # ← 这个文件 (唯一路线图)
├── todo.md                        # 每日任务
│
├── src/                           # 💻 自主代码
│   ├── week_1/                    # ROS2 + Panda (agibot_demo, panda_move...)
│   ├── week_2/                    # VLA仿真 (era3_vla_demo, vla_pipeline_sim...)
│   ├── week_3~6/                  # 各周仿真脚本
│   └── cloud_vla_bridge/          # 云端VLA桥接 (simulate_vla, panda_executor...)
│
├── docs/                          # 📚 文档
│   ├── solutions/                 # 敲门砖方案
│   └── reference/                 # 参考资料 + resume.md
│
├── third_party/                   # 📦 (当前为空，源码放在上层)
│
└── journal/                       # 📝 个人日志 (已gitignore)

上层根目录 (E:\0_1493677\11_AGIBOT\) 的已克隆资产:
├── 01_AIMA_genie_sim_code/        # genie_sim 完整版 (~2GB)
├── 02_genie_sim_lightweight/      # genie_sim 轻量版 (~70MB)
├── 03_lightweight_pack/           # 打包的轻量版 + openpi
├── ACoT-VLA/                      # CVPR 2026 VLA+思维链 (2.9M)
├── Genie-Envisioner/              # 世界模型平台 (52M)
├── genie_sim_architecture.md      # 架构分析文档
├── DataAgentParadigm.md           # 问数智能体范式
└── AgentForm.md                   # Agent 形态笔记
```

---

## 📎 相关文档索引

| 文档 | 路径 | 说明 |
|:---|:---|:---|
| 每日任务 | `todo.md` | ✅ 更新中 |
| 简历 | `docs/reference/resume.md` | ✅ 已写好，Week7打磨 |
| 敲门砖方案 | `docs/solutions/solution_loading_unloading.md` | ✅ |
| 三大场景ROI分析 | `docs/reference/high_roi_embodied_ai_scenarios.md` | ✅ |
| Genie Sim文档 | `docs/reference/Genie Sim User Guide.html` | 🟡 待读 |
| 代码部署指南 | `src/cloud_vla_bridge/deploy_to_autodl.md` | ✅ |
