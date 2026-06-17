# Day 10 · Genie Sim 3.0 动手（可选实操）

> 🟡 选做。做了面试加分，不做也不影响。
> 🕐 预计用时：2-3h

---

## 状态检查

Genie Sim 3.0 已开源在 `github.com/AgibotTech/genie_sim`。

⚠️ **可能的障碍**：
- 需要 NVIDIA GPU（Isaac Sim 底层依赖）
- WSL2 内 GPU 直通可能有限制
- 如果跑不起来——正常。把它当作「我调研过这个平台，知道它能做什么」就够

---

## 如果能跑

```bash
# 1. 克隆仓库
git clone https://github.com/AgibotTech/genie_sim.git
cd genie_sim

# 2. 按 README 安装依赖
# （需要 Docker 或 conda 环境，具体见官方文档）

# 3. 跑一个示例场景
# （官方应该提供了快速开始脚本）
```

---

## 如果跑不了（更可能的情况）

改成这个：

```bash
# 1. 看 Genie Sim 3.0 的 GitHub README（10 分钟）
#    - 看它有哪些功能
#    - 看它的示例场景截图
#    - 看它的 API 文档

# 2. 记笔记：它能做什么、你需要什么硬件
#    面试时提「我看过 Genie Sim 的 repo，它基于 Isaac Sim，
#    LLM 驱动场景生成，开源了 10000+ 小时仿真数据」

# 3. 替代方案：跑一个更轻量的仿真 demo
#    - 用你已有的 Panda Gazebo 仿真（已经跑通了！）
#    - 或者试试 MuJoCo（pip install mujoco，更轻量）
```

---

## 替代实操：OpenVLA 推理（更可行）

在 WSL 里跑一个开源 VLA 模型的推理：

```bash
# 安装
pip install transformers torch

# 下载 OpenVLA 模型（7B参数，需要 ~15GB 显存/内存）
# 如果 GPU 不够，用 Pi0 的小版本

# 或者更轻量：跑 RT-1 的推理（几百MB模型）
```

> 具体能跑什么取决于你的显卡。在你 WSL 里用 `nvidia-smi` 检查。

---

## 实操记录模板

```
平台：
尝试时间：
遇到的错误：
最终状态（能跑/跑不了）：
学到的东西：
面试怎么讲这 30 秒：
```

---

## 面试话术

> "我调研过 Genie Sim 3.0，它基于 NVIDIA Isaac Sim 做的一个上层仿真平台。它最大的创新是用大语言模型自动生成仿真场景——你说'给我一个 3C 工位'，它自动搭好环境。智元还开源了 10,000 多小时的仿真数据和 200 多个任务基准，这在具身智能领域目前是最大的开源仿真数据集。我在自己的环境上试过——（能跑就说跑通了，不能跑就说 WSL 不支持 GPU 直通但看过源码和文档）。"
