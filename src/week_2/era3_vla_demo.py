#!/usr/bin/env python3
"""
era3_vla_demo.py — Era 3 VLA 端到端推理仿真

让你在 Windows 上直接感受 VLA 的完整推理流程，不需要 GPU，不需要 ROS2。

核心演示：
  1. VLA (Era 3) 端到端：图片 → VLM 理解 → Action CoT → 关节角输出
  2. 对比 Era 2 (传统) ：视觉检测 → IK 求解 → 路径规划
  3. 展示 Era 3 的泛化能力 vs Era 2 的可靠性

用法：
  pip install numpy matplotlib
  python era3_vla_demo.py

面试话术：
  "我写过一个 VLA 端到端仿真，对比了 Era 3 和 Era 2 的决策差异。
   Era 3 的 VLA 从图片直接出关节角，靠数据隐式学 IK；
   Era 2 靠显式几何解算 IK。一个泛化强，一个精度高。"
"""

import numpy as np
import matplotlib.pyplot as plt
import time


# ============================================================
# 场景定义
# ============================================================

class Scene:
    def __init__(self, name, objects, task, lighting="normal", difficulty=0.5):
        self.name = name
        self.objects = objects
        self.task = task
        self.lighting = lighting
        self.difficulty = difficulty

    def describe(self):
        return f"场景: {self.name} | 物体: {', '.join(self.objects)} | 光照: {self.lighting}"


# ============================================================
# Era 2
# ============================================================

class Era2_Traditional:
    def __init__(self, name="Era 2 · 传统分治"):
        self.name = name

    def process(self, scene):
        result = {"method": self.name, "scene": scene.name,
                  "steps": [], "success": True, "total_latency_ms": 0}
        total_ms = 0

        # Step 1: 视觉检测
        s1 = 30 + np.random.rand() * 20
        total_ms += s1
        time.sleep(s1 / 1000)
        known = {"CPU芯片", "手机壳", "螺丝钉", "杯子"}
        detected = [o for o in scene.objects if o in known]
        missed = len(scene.objects) - len(detected)
        result["steps"].append({
            "name": "① 视觉检测 (YOLO)", "latency_ms": round(s1, 1),
            "output": f"检测到 {len(detected)}/{len(scene.objects)}" +
                     (f" ⚠️ 漏检 {missed}" if missed else "")
        })

        # Step 2: 位姿估算
        s2 = 20 + np.random.rand() * 15
        total_ms += s2
        time.sleep(s2 / 1000)
        result["steps"].append({
            "name": "② 位姿估算 (PnP)", "latency_ms": round(s2, 1),
            "output": "6D 位姿 (x,y,z,roll,pitch,yaw)"
        })

        # Step 3: IK 求解
        s3 = 5 + np.random.rand() * 10
        total_ms += s3
        time.sleep(s3 / 1000)
        ik_ok = True
        if scene.difficulty > 0.7:
            ik_ok = np.random.rand() > 0.3
        result["steps"].append({
            "name": "③ IK 求解", "latency_ms": round(s3, 1),
            "output": "✅ IK 有解" if ik_ok else "❌ IK 无解"
        })
        if not ik_ok:
            result["success"] = False
            result["total_latency_ms"] = round(total_ms, 1)
            return result

        # Step 4: 路径规划
        s4 = 50 + np.random.rand() * 100
        total_ms += s4
        time.sleep(s4 / 1000)
        path_ok = True
        if scene.difficulty > 0.6:
            path_ok = np.random.rand() > 0.2
        result["steps"].append({
            "name": "④ 路径规划 (RRT)", "latency_ms": round(s4, 1),
            "output": "✅ 路径找到" if path_ok else "❌ 路径规划失败"
        })
        result["success"] = path_ok
        result["total_latency_ms"] = round(total_ms, 1)
        return result


# ============================================================
# Era 3 VLA
# ============================================================

class Era3_VLA:
    def __init__(self, name="Era 3 · VLA 端到端"):
        self.name = name

    def process(self, scene):
        result = {"method": self.name, "scene": scene.name,
                  "steps": [], "success": True, "total_latency_ms": 0}
        total_ms = 0

        # ① 视觉编码
        s1 = 50 + np.random.rand() * 30
        total_ms += s1
        time.sleep(s1 / 1000)
        result["steps"].append({
            "name": "① 视觉编码 (ViT)", "latency_ms": round(s1, 1),
            "output": "图像 → 视觉 token 序列"
        })

        # ② VLM 场景理解
        s2 = 80 + np.random.rand() * 70
        total_ms += s2
        time.sleep(s2 / 1000)
        result["steps"].append({
            "name": "② VLM 场景理解", "latency_ms": round(s2, 1),
            "output": f'"{scene.describe()}" + 任务: "{scene.task}"'
        })

        # ③ Action CoT
        s3 = 30 + np.random.rand() * 20
        total_ms += s3
        time.sleep(s3 / 1000)
        if "抓" in scene.task:
            cot = ["🤔 识别目标位置", "🎯 计算抓取姿态",
                   "🖐️ 预张开夹爪", "📐 从上方接近"]
        else:
            cot = ["🤔 场景分析完成", "🎯 策略确定", "✅ 就绪"]
        result["steps"].append({
            "name": "③ Action CoT 思维链", "latency_ms": round(s3, 1),
            "output": "\n".join(f"     {s}" for s in cot)
        })

        # ④ 扩散生成关节角
        s4 = 40 + np.random.rand() * 30
        total_ms += s4
        time.sleep(s4 / 1000)

        base_success = 0.92
        if scene.lighting == "extreme":
            base_success -= 0.15
        if scene.difficulty > 0.7:
            base_success -= 0.10

        vla_ok = np.random.rand() < base_success
        joint_angles = np.round(np.random.randn(7) * 0.5, 3)

        result["steps"].append({
            "name": "④ 扩散生成关节角 (DiT)", "latency_ms": round(s4, 1),
            "output": f"7关节角: {joint_angles.tolist()}" if vla_ok else "❌ 推理失败"
        })
        if not vla_ok:
            result["success"] = False
            result["failure_reason"] = "VLA 泛化失败"
            result["total_latency_ms"] = round(total_ms, 1)
            return result

        # ⑤ 执行
        s5 = 10 + np.random.rand() * 5
        total_ms += s5
        time.sleep(s5 / 1000)
        result["steps"].append({
            "name": "⑤ 关节执行", "latency_ms": round(s5, 1),
            "output": f"执行完成 ({round(total_ms,1)}ms)"
        })
        result["success"] = True
        result["total_latency_ms"] = round(total_ms, 1)
        return result


# ============================================================
# 运行对比
# ============================================================

def run_comparison():
    scenes = [
        Scene("仓储物流", ["CPU芯片", "泡沫垫"], "抓取 CPU 芯片放到传送带",
              lighting="normal", difficulty=0.3),
        Scene("制造产线", ["手机壳", "螺丝钉"], "抓取手机壳放到夹具",
              lighting="normal", difficulty=0.8),
        Scene("农业采摘", ["番茄", "叶子"], "抓取成熟番茄",
              lighting="extreme", difficulty=0.6),
        Scene("新物体泛化", ["异形工件"], "抓取未知工件放到料框",
              lighting="normal", difficulty=0.7),
    ]

    era2 = Era2_Traditional()
    era3 = Era3_VLA()

    print("\n" + "=" * 70)
    print("  🆚 Era 2 vs Era 3 对比")
    print("=" * 70)

    for i, scene in enumerate(scenes):
        print(f"\n{'─'*70}")
        print(f"  场景 {i+1}: {scene.name}")
        print(f"  物体: {', '.join(scene.objects)} | 任务: {scene.task}")
        print(f"{'─'*70}")

        r2 = era2.process(scene)
        print(f"\n  {era2.name}")
        for s in r2["steps"]:
            print(f"    {s['name']} ({s['latency_ms']}ms) → {s['output']}")
        print(f"  {'✅' if r2['success'] else '❌'} | {r2['total_latency_ms']}ms")

        r3 = era3.process(scene)
        print(f"\n  {era3.name}")
        for s in r3["steps"]:
            out = s['output'].replace('\n', '\n        ')
            print(f"    {s['name']} ({s['latency_ms']}ms) → {out}")
        print(f"  {'✅' if r3['success'] else '❌'} | {r3['total_latency_ms']}ms")


def visualize_architecture():
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    # Era 2
    ax[0].set_xlim(0, 10)
    ax[0].set_ylim(0, 6)
    ax[0].set_title("🏗️  Era 2 · 模块化分治", fontsize=14, fontweight='bold')
    ax[0].axis('off')

    boxes = [
        (1, 4.5, "📷 视觉检测\nYOLO", "#D4E6F1"),
        (1, 2.5, "🧮 IK 求解\n数值法", "#D5F5E3"),
        (5.5, 4.5, "🎯 位姿估算\nPnP", "#FCF3CF"),
        (5.5, 2.5, "🗺️ 路径规划\nRRT", "#FADBD8"),
        (3, 0.5, "🤖 执行\nPID控制", "#E8DAEF"),
    ]
    for x, y, label, color in boxes:
        rect = plt.Rectangle((x, y), 4, 1.2, facecolor=color,
                             edgecolor='#2C3E50', linewidth=2, alpha=0.8)
        ax[0].add_patch(rect)
        ax[0].text(x+2, y+0.6, label, ha='center', va='center', fontsize=9)

    # Era 3
    ax[1].set_xlim(0, 10)
    ax[1].set_ylim(0, 6)
    ax[1].set_title("🧠  Era 3 · VLA 端到端", fontsize=14, fontweight='bold')
    ax[1].axis('off')

    boxes3 = [
        (0.5, 4.5, "🐢 慢系统 System 2\nVLM + Action CoT\n~7-10Hz", "#AED6F1"),
        (5.5, 2.5, "🐇 快系统 System 1\nDiT 扩散关节角\n~50Hz", "#A9DFBF"),
        (3, 0.5, "🤖 执行\n关节控制", "#E8DAEF"),
    ]
    for x, y, label, color in boxes3:
        rect = plt.Rectangle((x, y), 4, 1.2, facecolor=color,
                             edgecolor='#2C3E50', linewidth=2, alpha=0.8)
        ax[1].add_patch(rect)
        ax[1].text(x+2, y+0.6, label, ha='center', va='center', fontsize=9)

    plt.suptitle("Era 2 vs Era 3: 模块化 vs 端到端", fontsize=16, y=1.02)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print()
    print("╔" + "═" * 60 + "╗")
    print("║" + "  🧠 Era 3 VLA 端到端推理仿真".center(60) + "║")
    print("╚" + "═" * 60 + "╝")

    while True:
        print("\n  1. 🆚 Era 2 vs Era 3 场景对比")
        print("  2. 📊 可视化架构对比图")
        print("  3. 📋 打印总结表")
        print("  0. 🚪 退出")
        choice = input("  输入编号: ").strip()

        if choice == "1":
            run_comparison()
        elif choice == "2":
            try:
                visualize_architecture()
            except Exception as e:
                print(f"  ⚠️ 需要 GUI: {e}")
        elif choice == "3":
            print("\n📋 Era 2 vs Era 3 总结")
            print(f"{'维度':<20} {'Era 2':<25} {'Era 3':<25}")
            print(f"{'─'*20} {'─'*25} {'─'*25}")
            print(f"{'决策':<20} {'独立模块串联':<25} {'单一模型端到端':<25}")
            print(f"{'视觉':<20} {'YOLO+模板匹配':<25} {'ViT直接编码':<25}")
            print(f"{'路径':<20} {'RRT显式规划':<25} {'隐式从数据学':<25}")
            print(f"{'IK':<20} {'数值/解析求解':<25} {'隐式内化':<25}")
            print(f"{'延迟':<20} {'~105-185ms':<25} {'~210-350ms':<25}")
            print(f"{'精度':<20} {'⭐⭐⭐⭐⭐':<25} {'⭐⭐⭐':<25}")
            print(f"{'泛化':<20} {'⭐⭐':<25} {'⭐⭐⭐⭐':<25}")
        elif choice == "0":
            print("\n  👋 再见！\n")
            break
