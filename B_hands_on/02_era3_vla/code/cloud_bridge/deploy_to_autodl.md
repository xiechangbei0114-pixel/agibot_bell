# ☁️ AutoDL 部署 VLA 推理服务器

> 当你准备好租云 GPU 时，按这个步骤操作

---

## 1. 注册 + 租 GPU

1. 打开 [AutoDL](https://www.autodl.com/) 注册
2. 选择镜像：**PyTorch 2.x + CUDA 12.x**（选最新的就行）
3. 选择 GPU：
   - 入门：RTX 4090（~¥4/h）→ 能跑 Pi0.5 / OpenVLA
   - 省钱：RTX 3090（~¥2/h）→ 能跑小模型
4. 开机后打开 **Jupyter Lab** 或 **SSH 连接**

---

## 2. 部署推理服务

在 AutoDL 的终端里执行：

```bash
# 安装依赖
pip install torch transformers websockets openpi-pipeline

# 拉取推理服务器代码（我们在 GitHub 上有一个轻量服务器）
git clone https://github.com/your-account/vla-inference-server.git
cd vla-inference-server

# 启动推理服务
python3 server.py --model pi0 --port 8765
```

> 如果不想自己搭，也可以用智元的云端 API（Genie Studio 的推理接口）

---

## 3. 本地连接

在 AutoDL 的控制台找到 **公网 IP** 和 **端口映射**（比如 `123.45.67.89:6006`）：

```bash
# 在你本机 WSL 里运行桥接器
python3 cloud_vla_bridge/vla_cloud_bridge.py --ws ws://123.45.67.89:6006
```

---

## 4. 完整 Demo 流程

```
终端 1 (WSL):                    终端 2 (WSL):
ros2 launch ...                   python3 cloud_vla_bridge/
  panda_gazebo                      panda_executor.py

终端 3 (WSL):                    云端 (AutoDL):
python3 cloud_vla_bridge/         python3 server.py
  vla_cloud_bridge.py               --model pi0
  --ws ws://xxx:6006
```

---

## 5. 先试试本地模拟版

不想花钱的话，直接用 `simulate_vla.py` + `panda_executor.py` 就能跑通**完整链路**：

```bash
# WSL 终端 1: 启动 Panda 仿真（你得先有）
ros2 launch panda_moveit_config panda_gazebo.launch.py

# WSL 终端 2: 启动 VLA 模拟（不需要 GPU）
python3 cloud_vla_bridge/simulate_vla.py

# WSL 终端 3: 启动执行器
python3 cloud_vla_bridge/panda_executor.py

# WSL 终端 4: 手动触发来料测试
ros2 topic pub /parts_detected std_msgs/msg/String "data: '1|CPU芯片|0.02|-0.01'"
```

也能启动产线 Demo 自动发来料：
```bash
# 终端 5: 产线模拟器（每 3 秒自动来料）
python3 week_1/agibot_demo.py
```
