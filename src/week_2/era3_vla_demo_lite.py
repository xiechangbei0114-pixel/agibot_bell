#!/usr/bin/env python3
"""
era3_vla_demo_lite.py — Era 3 VLA 端到端推理仿真（轻量版，无需 numpy/matplotlib）

直接在 Windows 上跑，不需要任何第三方库：
  python era3_vla_demo_lite.py
"""

import time
import random
import os
import sys


# ============================================================
# 场景定义
# ============================================================

SCENES = [
    {
        "name": "仓储物流",
        "objects": ["CPU芯片", "泡沫垫"],
        "task": "抓取 CPU 芯片放到传送带",
        "lighting": "normal",
        "difficulty": 0.3,
        "desc": "品种多(200+)，精度低(2cm OK)，节拍慢(10-15s)"
    },
    {
        "name": "制造产线",
        "objects": ["手机壳", "螺丝钉"],
        "task": "抓取手机壳放到夹具",
        "lighting": "normal",
        "difficulty": 0.8,
        "desc": "品种少(<5)，精度高(0.5mm)，节拍快(<3s)"
    },
    {
        "name": "农业采摘",
        "objects": ["番茄", "叶子"],
        "task": "抓取成熟番茄",
        "lighting": "extreme",
        "difficulty": 0.6,
        "desc": "环境变化大，光照不稳定，容错率高"
    },
    {
        "name": "新物体泛化",
        "objects": ["异形工件"],
        "task": "抓取未知工件放到料框",
        "lighting": "normal",
        "difficulty": 0.7,
        "desc": "VLA 没训练过的工件，考验泛化能力"
    },
]


# ============================================================
# Era 2 传统方法
# ============================================================

class Era2:
    """Era 2 传统分治：多个独立模块串联"""

    NAME = "🏗️  Era 2 · 传统分治"

    @staticmethod
    def run(scene):
        steps = []
        total_ms = 0
        success = True

        # ① 视觉检测
        latency = round(30 + random.random() * 20, 1)
        total_ms += latency
        known = {"CPU芯片", "手机壳", "螺丝钉", "杯子"}
        detected = [o for o in scene["objects"] if o in known]
        missed = len(scene["objects"]) - len(detected)
        steps.append(("① 视觉检测 (YOLO)", latency,
                      f"检测到 {len(detected)}/{len(scene['objects'])} 个物体" +
                      (f" ⚠️ 漏检 {missed} 个" if missed else " ✅")))

        # ② 位姿估算
        latency = round(20 + random.random() * 15, 1)
        total_ms += latency
        steps.append(("② 位姿估算 (PnP)", latency, "输出 6D 位姿"))

        # ③ IK 求解
        latency = round(5 + random.random() * 10, 1)
        total_ms += latency
        ik_ok = True
        if scene["difficulty"] > 0.7:
            ik_ok = random.random() > 0.3
        steps.append(("③ IK 求解", latency,
                      "✅ IK 有解" if ik_ok else "❌ IK 无解"))
        if not ik_ok:
            return steps, round(total_ms, 1), False, "IK 无解"

        # ④ 路径规划
        latency = round(50 + random.random() * 100, 1)
        total_ms += latency
        path_ok = True
        if scene["difficulty"] > 0.6:
            path_ok = random.random() > 0.2
        steps.append(("④ 路径规划 (RRT)", latency,
                      "✅ 路径找到" if path_ok else "❌ 路径规划失败"))
        if not path_ok:
            return steps, round(total_ms, 1), False, "路径规划失败"

        return steps, round(total_ms, 1), True, "成功"


# ============================================================
# Era 3 VLA 端到端
# ============================================================

class Era3:
    """Era 3 VLA 端到端：单一模型完成所有步骤"""

    NAME = "🧠  Era 3 · VLA 端到端"

    @staticmethod
    def run(scene):
        steps = []
        total_ms = 0

        # ① 视觉编码 (ViT)
        latency = round(50 + random.random() * 30, 1)
        total_ms += latency
        steps.append(("① 视觉编码 (ViT)", latency, "图像 → 视觉 token 序列"))

        # ② VLM 场景理解
        latency = round(80 + random.random() * 70, 1)
        total_ms += latency
        obj_desc = ", ".join(scene["objects"])
        steps.append(("② VLM 场景理解", latency,
                      f'场景: {scene["name"]} | 物体: {obj_desc}'))

        # ③ Action CoT
        latency = round(30 + random.random() * 20, 1)
        total_ms += latency
        if "抓" in scene["task"]:
            cot = ["🤔 识别目标位置", "🎯 计算抓取姿态 → 末端朝下45°",
                   "🖐️ 预张开夹爪至 80mm", "📐 从上方接近 → 避开障碍"]
        else:
            cot = ["🤔 场景分析完成", "🎯 最优策略确定", "✅ 动作序列就绪"]
        steps.append(("③ Action CoT 思维链", latency, " → ".join(cot)))

        # ④ 扩散生成关节角
        latency = round(40 + random.random() * 30, 1)
        total_ms += latency

        base_rate = 0.92
        if scene["lighting"] == "extreme":
            base_rate -= 0.15
        if scene["difficulty"] > 0.7:
            base_rate -= 0.10

        vla_ok = random.random() < base_rate
        joint_angles = [round(random.gauss(0, 0.5), 3) for _ in range(7)]

        if vla_ok:
            steps.append(("④ 扩散生成关节角 (DiT)", latency,
                          f"7关节角: {joint_angles} ✅"))
        else:
            steps.append(("④ 扩散生成关节角 (DiT)", latency, "❌ 推理失败"))
            return steps, round(total_ms, 1), False, "VLA 泛化失败"

        # ⑤ 执行
        latency = round(10 + random.random() * 5, 1)
        total_ms += latency
        steps.append(("⑤ 关节执行", latency, f"执行完成 ({round(total_ms,1)}ms)"))

        return steps, round(total_ms, 1), True, "成功"


# ============================================================
# 显示函数
# ============================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text):
    width = 70
    print()
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


def mode_compare():
    clear_screen()
    for i, scene in enumerate(SCENES):
        print_header(f"📦 场景 {i+1}: {scene['name']}")
        print(f"  物体: {', '.join(scene['objects'])}")
        print(f"  任务: {scene['task']}")
        print(f"  特征: {scene['desc']}")
        print(f"  难度: {scene['difficulty']} | 光照: {scene['lighting']}")
        print(f"{'─'*70}")

        s2, t2, ok2, r2 = Era2.run(scene)
        icon2 = "✅" if ok2 else "❌"
        print(f"\n  {Era2.NAME}")
        for s in s2:
            print(f"    {s[0]} ({s[1]}ms) → {s[2]}")
        print(f"  {icon2} {'成功' if ok2 else f'失败: {r2}'} | {t2}ms")

        s3, t3, ok3, r3 = Era3.run(scene)
        icon3 = "✅" if ok3 else "❌"
        print(f"\n  {Era3.NAME}")
        for s in s3:
            print(f"    {s[0]} ({s[1]}ms) → {s[2]}")
        print(f"  {icon3} {'成功' if ok3 else f'失败: {r3}'} | {t3}ms")

        diff = abs(t2 - t3)
        faster = "Era 2 快" if t2 < t3 else "Era 3 快"
        print(f"\n  📊 延迟: {t2}ms vs {t3}ms ({faster} {diff:.0f}ms)")

        if ok2 and not ok3:
            print(f"  ⚠️ 结论: VLA 翻车 → 需要兜底")
        elif not ok2 and ok3:
            print(f"  💪 结论: VLA 泛化成功！传统方案失败")
        elif ok2 and ok3:
            print(f"  ✅ 结论: 两者都成功")
        else:
            print(f"  ❌ 结论: 都失败 → 人工介入")

        input(f"\n  ⏎ 按 Enter 看下个场景...")
        clear_screen()


def mode_arch():
    clear_screen()
    print_header("🏗️  Era 2 架构 · 模块化分治")
    print("""
  ┌─────────────┐    ┌─────────────┐
  │ 视觉检测     │    │ 位姿估算     │
  │ YOLO+模板匹配 │    │ PnP 算法    │
  └──────┬──────┘    └──────┬──────┘
         ▼                  ▼
  ┌─────────────┐    ┌─────────────┐
  │ IK 求解     │    │ 路径规划    │
  │ 数值法      │    │ RRT/MoveIt  │
  └──────┬──────┘    └──────┬──────┘
         └────────┬─────────┘
                  ▼
         ┌──────────────┐
         │ 关节执行      │
         └──────────────┘
    """)
    input("  ⏎ 按 Enter 看 Era 3...")
    clear_screen()
    print_header("🧠  Era 3 · VLA 端到端")
    print("""
  ┌──────────────────────────────┐
  │ 🐢 慢系统 System 2 (~7-10Hz) │
  │  VLM 场景理解 + Action CoT   │
  └──────────────┬───────────────┘
                 ▼
  ┌──────────────────────────────┐
  │ 🐇 快系统 System 1 (~50Hz)   │
  │  DiT 扩散生成 7 关节角       │
  └──────────────┬───────────────┘
                 ▼
  ┌──────────────────────────────┐
  │ 🤖 执行 + 力反馈             │
  └──────────────────────────────┘
  Era 2: 看到→算位姿→算IK→规划路径→执行
  Era 3: 看到→模型直接出关节角→执行
  """)
    input("  ⏎ 按 Enter 返回...")


def main():
    while True:
        clear_screen()
        print()
        print("╔" + "═" * 60 + "╗")
        print("║" + "  🧠 Era 3 VLA 端到端推理仿真 (轻量版)".center(60) + "║")
        print("╚" + "═" * 60 + "╝")
        print()
        print("  1. 🆚 Era 2 vs Era 3 场景对比")
        print("  2. 📊 架构对比讲解")
        print("  3. 📋 退出")
        print()

        choice = input("  输入编号: ").strip()
        if choice == "1":
            mode_compare()
        elif choice == "2":
            mode_arch()
        elif choice == "0":
            print("\n  👋 再见！\n")
            break
        else:
            print("  ❌ 无效输入")


if __name__ == "__main__":
    main()
