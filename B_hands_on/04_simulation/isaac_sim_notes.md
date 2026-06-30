# Isaac Sim / Isaac Lab 仿真记录

> 用于记录 Isaac Sim 和 Isaac Lab 的云GPU环境搭建、仿真测试进度和技术笔记。
> 目标：验证 VLA 策略在仿真环境中的可行性，为真机部署做准备。

---

## 一、云 GPU 服务商对比

| 服务商 | A10 价格 | 免费额度 | Isaac Sim 支持 | 状态 |
|:---|:---:|:---:|:---:|:---:|
| **isaaclab.info** | — | — | 自带 Isaac Sim 镜像 | 🎯 正在使用 |
| **金山云** | ¥10/h | 送 ¥1500（3个月） | 待验证 | ⏳ 备选，未开通 |
| **阿里云** | ¥10/h | 送 ¥1500（3个月） | 待验证 | ❌ 创建两次均资源不足 |
| 腾讯云 | — | — | — | ❌ GPU 被租完 |
| AutoDL | — | — | ❌ 无 Isaac Sim 镜像 | ❌ |

### isaaclab.info（当前正在用）

- **费用：** 未知（按量计费）
- **状态：** 🎯 已开通，机器正在运行
- **优点：** 自带 Isaac Sim 镜像，开箱即用
- **连接方式：** isaaclab.info 自带的远程客户端（非SSH直连）
- **问题记录：**
  - 之前觉得简陋不稳定，实际能用
  - 通过远程客户端启动 Isaac Sim，拖了几个机器人进去 ✅
  - 远程连接本身够用，但后续开发（跑预训练模型推理）需确认 Python API 是否通

### 金山云（备选）

- **费用：** A10 ¥10/h，送 ¥1500 ≈ 150h 免费额度
- **状态：** ⏳ 未开通，备选方案
- **问题记录：**
  - 

### 阿里云（放弃）

- **费用：** A10 ¥10/h，送 ¥1500
- **状态：** ❌ 已放弃
- **问题记录：**
  - 第一次创建：资源不足
  - 第二次创建：依然资源不足
  - 需要走集群服务，配置复杂，即使开通也可能抢不到资源

---

## 二、Isaac Sim 环境搭建

### 系统要求

| 组件 | 最低要求 | 推荐 |
|:---|:---|:---|
| GPU | RTX 3060 | RTX 4090 / A10 / A100 |
| VRAM | 8 GB | 24 GB+ |
| 驱动 | NVIDIA Driver 525+ | 545+ |
| CUDA | 11.8 | 12.x |
| 系统 | Ubuntu 20.04 / 22.04 | Ubuntu 22.04 |

### 安装记录

#### 方法一：Native 安装

```bash
# 待验证
```

#### 方法二：Docker 安装

```bash
# 待验证
```

#### 方法三：云镜像

- **isaaclab.info：** ✅ 自带 Isaac Sim 镜像，直接用
- **金山云：** 是否有 Isaac Sim 镜像？→ ⏳ 备选，待确认

---

## 三、Isaac Lab 环境搭建

### 安装步骤

```bash
# 待验证
```

### 依赖项

- [ ] Isaac Sim 2023.1.1 / 2024.x
- [ ] Python 3.10+
- [ ] PyTorch 2.x
- [ ] CUDA 12.x

---

## 四、仿真实验记录

### 实验 1：Panda 机械臂抓取

| 项目 | 内容 |
|:---|:---|
| 场景 | 桌面物体抓取 |
| 机械臂 | Franka Panda (7-DOF) |
| 控制器 | 待选 |
| 状态 | ✅ 已启动 Isaac Sim，拖入机器人，验证 GUI 基本操作 |

### 实验 2：VLA 策略部署到仿真（待开始）

| 项目 | 内容 |
|:---|:---|
| 策略 | GO-2 / OpenPI / GR00T |
| 环境 | Isaac Lab |
| 状态 | ⏳ 未开始 |

### 实验 3：GR00T 预训练模型推理测试

| 项目 | 内容 |
|:---|:---|
| 策略 | NVIDIA GR00T-N1.7-3B |
| 数据 | `third_party/gr00t/demo_data/droid_sample`（现成 demo 数据）|
| 脚本 | `third_party/gr00t/getting_started/GR00T_inference.ipynb` |
| 状态 | 🎯 **明晚（06.26）目标：跑通推理** |

**计划步骤：**
1. 在 isaaclab.info 远程机器上安装 gr00t（`pip install -e .`）
2. 运行 `GR00T_inference.ipynb`，加载预训练模型 + demo 数据
3. 验证模型能输出 action
4. 如果时间够：尝试在 Isaac Sim 里用 ROS2 bag 录一条自己的 demo

---

## 五、问题与解决方案

### 待解决问题

1. **云 GPU 环境缺少 Isaac Sim 镜像**
   - 方案：手动安装或用 Docker
   - 优先级：高
2. **阿里云/腾讯云 GPU 资源不足**
   - 金山云是唯一可能的选择
   - 优先级：高
2. **Isaac Sim 硬件要求高**
   - A10 (24GB) 是否够用？
   - 优先级：中

### 已解决问题

1. **isaaclab.info 远程连接**
   - 已通过其自带远程客户端成功连接到 GPU 机器 ✅
   - 已启动 Isaac Sim，验证 GUI 可操作
2. **"连上远程后不知道下一步"**
   - 已理清方向：方案岗不需要自己训 RL/IL，用现成预训练模型跑推理即可
   - 已确定明晚目标：跑通 GR00T 预训练模型推理 demo

---

## 六、参考链接

- [NVIDIA Isaac Sim 官方文档](https://docs.omniverse.nvidia.com/isaacsim/latest/overview.html)
- [Isaac Lab 文档](https://isaac-sim.github.io/IsaacLab/)
- [金山云 GPU 实例](https://www.ksyun.com/)
- [阿里云 GPU 实例](https://www.aliyun.com/)

---

## 更新日志

| 日期 | 更新内容 |
|:---|:---|
| 2026-06-25 | 创建文档，记录云 GPU 服务商对比，初始化环境搭建模板 |
| 2026-06-25 | 阿里云创建两次均资源不足，放弃。转向金山云作为唯一途径 |
| 2026-06-25 | 实际使用 isaaclab.info（之前误判简陋，实际可用），纠正记录 |
| 2026-06-25 | 通过远程客户端连上 isaaclab.info，启动 Isaac Sim，拖入机器人验证 GUI ✅ |
| 2026-06-25 | 明确方案岗路径：不自己训 RL/IL，用预训练模型（GR00T/Pi0）跑推理 |
| 2026-06-25 | 新增实验3目标：明晚跑通 GR00T-N1.7 预训练模型推理 demo |
