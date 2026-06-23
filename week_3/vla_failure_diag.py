#!/usr/bin/env python3
"""
vla_failure_diag.py — VLA 故障诊断树（交互式 CLI + 可视化）

功能：
  1. 交互式 CLI 诊断：输入故障症状，输出根因分析 + 修复建议
  2. 故障树可视化：matplotlib 绘制完整故障诊断决策树
  3. 各场景（仓储/制造/农业）的故障模式分布对比
  4. 五层兜底链模拟

用法：
  pip install numpy matplotlib
  python vla_failure_diag.py

面试话术：「我设计了 VLA 故障诊断树——当产线 VLA 翻车时，
            能 5 分钟内定位到根因，而不是一头扎进模型训练里。」
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from typing import List, Dict, Optional, Tuple
import json


# ============================================================
# Part 1: 故障知识库
# ============================================================

FAILURE_KB = {
    "抓取失败 (Grasp Failure)": {
        "description": "机械臂到达目标位置但无法抓取/夹取时滑落",
        "symptoms": ["末端执行器到位但夹不住", "物体滑落", "抓取力不足"],
        "severity": "high",
        "possible_causes": [
            {
                "cause": "夹爪力控参数不当",
                "probability": 0.35,
                "layer": "L4 执行层",
                "check": "检查 gripper 力矩设定值是否在工件规格内",
                "fix": "调整夹爪力控 PID 参数或更换对应工件型号的夹爪",
            },
            {
                "cause": "VLA 姿态估算偏差 > 5mm",
                "probability": 0.25,
                "layer": "L2 推理层",
                "check": "验证抓取姿态与真值偏差",
                "fix": "增加该工件的训练数据配重或添加姿态校验规则",
            },
            {
                "cause": "物体材质/形状超出泛化范围",
                "probability": 0.20,
                "layer": "L1 感知层",
                "check": "确认物体是否在训练数据覆盖范围内",
                "fix": "补充该材质/形状的仿真数据",
            },
            {
                "cause": "夹爪/末端磨损",
                "probability": 0.10,
                "layer": "L5 硬件层",
                "check": "目视检查夹爪磨损情况",
                "fix": "更换夹爪橡胶垫/维修",
            },
            {
                "cause": "协同: IK 精度不足",
                "probability": 0.10,
                "layer": "L3 规划层",
                "check": "检查 IK solver 误差",
                "fix": "添加 IK 校验后置条件",
            },
        ],
    },
    "定位偏差 (Position Deviation)": {
        "description": "末端到达位置偏离目标 > 3mm",
        "symptoms": ["装配对不准", "螺丝歪斜", "插入失败"],
        "severity": "high",
        "possible_causes": [
            {
                "cause": "视觉标定漂移",
                "probability": 0.30,
                "layer": "L1 感知层",
                "check": "运行手眼标定验证程序",
                "fix": "重新执行 Eye-in-Hand 标定",
            },
            {
                "cause": "VLM 视觉 grounding 误差",
                "probability": 0.25,
                "layer": "L2 推理层",
                "check": "对比 VLM 检测框与 ground truth",
                "fix": "添加视觉 grounding 校验模块或回退到传统视觉",
            },
            {
                "cause": "运动学参数误差（连杆/关节）",
                "probability": 0.15,
                "layer": "L3 规划层",
                "check": "运行运动学标定程序",
                "fix": "更新 URDF 运动学参数",
            },
            {
                "cause": "关节零位漂移",
                "probability": 0.20,
                "layer": "L4 执行层",
                "check": "检查编码器零位",
                "fix": "重新校准关节零位",
            },
            {
                "cause": "地面/安装基座松动",
                "probability": 0.10,
                "layer": "L5 硬件层",
                "check": "检查基座螺栓扭矩",
                "fix": "紧固螺栓",
            },
        ],
    },
    "决策超时 (Decision Timeout)": {
        "description": "VLA 推理时间超过产线节拍限制",
        "symptoms": ["产线停顿", "节拍超标", "VLA 无响应"],
        "severity": "medium",
        "possible_causes": [
            {
                "cause": "VLM 模型过大/计算资源不足",
                "probability": 0.35,
                "layer": "L2 推理层",
                "check": "监控 GPU 利用率与推理耗时",
                "fix": "模型量化/蒸馏或升级计算硬件",
            },
            {
                "cause": "视觉输入分辨率过高",
                "probability": 0.20,
                "layer": "L1 感知层",
                "check": "检查输入图像分辨率",
                "fix": "降低分辨率或 ROI 裁剪",
            },
            {
                "cause": "网络延迟（云推理）",
                "probability": 0.25,
                "layer": "L0 通信层",
                "check": "ping 云服务器延迟",
                "fix": "切换本地推理或优化网络 QoS",
            },
            {
                "cause": "动作 token 解码卡死",
                "probability": 0.20,
                "layer": "L2 推理层",
                "check": "检查 token 解码循环",
                "fix": "添加解码超时熔断 (timeout=500ms)",
            },
        ],
    },
    "碰撞/干涉 (Collision)": {
        "description": "机械臂与周围物体发生碰撞",
        "symptoms": ["碰撞检测触发", "异常力矩", "急停"],
        "severity": "critical",
        "possible_causes": [
            {
                "cause": "VLA 规划路径未考虑障碍物",
                "probability": 0.25,
                "layer": "L2 推理层",
                "check": "检查 VLA 输出的路径点",
                "fix": "添加碰撞检测后处理 + 路径重规划",
            },
            {
                "cause": "场景变化（新物体出现）",
                "probability": 0.20,
                "layer": "L1 感知层",
                "check": "对比场景变化检测",
                "fix": "更新场景语义地图",
            },
            {
                "cause": "规划层碰撞检测未生效",
                "probability": 0.20,
                "layer": "L3 规划层",
                "check": "确认 MoveIt 碰撞检测启用",
                "fix": "启用 PlanningScene 更新",
            },
            {
                "cause": "工件/夹具安装偏移",
                "probability": 0.15,
                "layer": "L5 硬件层",
                "check": "检查工件位置一致性",
                "fix": "校准工件夹具",
            },
            {
                "cause": "协同: MES 给错工件位置",
                "probability": 0.20,
                "layer": "L0 通信层",
                "check": "核对 MES 下发坐标",
                "fix": "添加工位视觉二次确认",
            },
        ],
    },
}


# ============================================================
# Part 2: 交互式 CLI 诊断
# ============================================================

class FailureDiagnosis:
    """交互式故障诊断"""

    def __init__(self):
        self.kb = FAILURE_KB

    def list_failure_types(self) -> List[str]:
        return list(self.kb.keys())

    def diagnose(self, symptom: str) -> Optional[Dict]:
        """根据症状匹配故障类型"""
        symptom_lower = symptom.lower()
        best_match = None
        best_score = 0

        for ftype, finfo in self.kb.items():
            for s in finfo["symptoms"]:
                # 简单的关键词匹配
                score = len(set(symptom_lower.split()) & set(s.lower().split()))
                if score > best_score:
                    best_score = score
                    best_match = ftype

        if best_match and best_score > 0:
            return self.get_diagnosis(best_match)
        return None

    def get_diagnosis(self, failure_type: str) -> Dict:
        """获取某个故障的完整诊断"""
        finfo = self.kb[failure_type]
        causes = sorted(finfo["possible_causes"],
                       key=lambda x: x["probability"], reverse=True)

        return {
            "failure_type": failure_type,
            "description": finfo["description"],
            "severity": finfo["severity"],
            "symptoms": finfo["symptoms"],
            "causes": causes,
            "top_cause": causes[0],
            "layers_involved": list(set(c["layer"] for c in causes)),
        }

    def interactive_diagnosis(self):
        """交互式诊断对话"""
        print("\n" + "=" * 70)
        print("🔍 VLA 故障诊断树 — 交互模式")
        print("=" * 70)

        print("\n可诊断的故障类型：")
        for i, ft in enumerate(self.list_failure_types(), 1):
            print(f"  {i}. {ft}")
        print(f"  {len(self.list_failure_types()) + 1}. 输入自己的症状")

        try:
            choice = int(input(f"\n请选择 [1-{len(self.list_failure_types()) + 1}]: ") or "0")
        except:
            choice = 0

        if 1 <= choice <= len(self.list_failure_types()):
            ftype = self.list_failure_types()[choice - 1]
        elif choice == len(self.list_failure_types()) + 1:
            symptom = input("描述症状: ")
            result = self.diagnose(symptom)
            if result:
                ftype = result["failure_type"]
                print(f"\n→ 匹配到故障类型: {ftype}")
            else:
                print("❌ 无法识别症状，请扩展故障知识库")
                return
        else:
            return

        diag = self.get_diagnosis(ftype)
        self._print_diagnosis(diag)

    def _print_diagnosis(self, diag: Dict):
        """打印诊断结果"""
        severity_color = {
            "critical": "🔴 致命",
            "high": "🟠 严重",
            "medium": "🟡 中等",
            "low": "🟢 轻微",
        }

        print(f"\n{'='*70}")
        print(f"📋 诊断报告")
        print(f"{'='*70}")
        print(f"故障类型: {diag['failure_type']}")
        print(f"严重程度: {severity_color.get(diag['severity'], diag['severity'])}")
        print(f"故障描述: {diag['description']}")
        print(f"涉及层次: {', '.join(diag['layers_involved'])}")

        print(f"\n📊 根因概率排序：")
        print(f"  {'原因':30s} {'概率':8s} {'层次':12s} {'修复建议'}")
        print(f"  {'-'*30} {'-'*8} {'-'*12} {'-'*30}")
        for c in diag["causes"]:
            print(f"  {c['cause']:30s} {c['probability']*100:6.1f}%  {c['layer']:12s} {c['fix'][:30]}...")

        print(f"\n🎯 最大可能根因: {diag['top_cause']['cause']} ({diag['top_cause']['layer']})")
        print(f"   检查方法: {diag['top_cause']['check']}")
        print(f"   修复方案: {diag['top_cause']['fix']}")

        print(f"\n🔄 诊断路径（决策树）：")
        self._print_tree(diag, indent=0)

    def _print_tree(self, diag: Dict, indent: int=0):
        """打印决策树路径"""
        prefix = "  " * indent
        print(f"{prefix}├─ 症状: {diag['symptoms'][0]}")
        for i, c in enumerate(diag["causes"][:3]):
            branch = "├─" if i < 2 else "└─"
            print(f"{prefix}{branch} 检查 {c['layer']}: {c['check'][:40]}...")
            if c['probability'] > 0.25:
                print(f"{prefix}│  └─ ✅ 根因: {c['cause']} → {c['fix'][:40]}...")
            else:
                print(f"{prefix}│  └─ ❌ 不是 → 检查下一层")


# ============================================================
# Part 3: 可视化
# ============================================================

def visualize_failure_tree():
    """故障树可视化"""
    diag = FailureDiagnosis()
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')

    title = ax.text(8, 9.5, 'VLA 故障诊断树 — 五层兜底链',
                    ha='center', fontsize=16, fontweight='bold', color='#64ffda')

    # 五层架构
    layers = [
        ("L0: 通信层", "网络 / MES / 协议", 0, "#ff5252"),
        ("L1: 感知层", "视觉 / 标定 / 场景", 1.5, "#ff8a65"),
        ("L2: 推理层", "VLM / Tokenizer", 3.0, "#4fc3f7"),
        ("L3: 规划层", "IK / 碰撞检测", 4.5, "#81c784"),
        ("L4: 执行层", "力控 / 轨迹跟踪", 6.0, "#ffd600"),
        ("L5: 硬件层", "关节 / 夹爪 / 基座", 7.5, "#ce93d8"),
    ]

    def draw_layer_box(y_pos, name, desc, color):
        box = FancyBboxPatch((0.5, y_pos), 4.5, 1.2,
                             boxstyle="round,pad=0.1",
                             facecolor=color + "15", edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(2.75, y_pos + 0.7, name, ha='center', va='center',
                fontsize=12, fontweight='bold', color='white')
        ax.text(2.75, y_pos + 0.25, desc, ha='center', va='center',
                fontsize=9, color='#a8b2d1')
        return y_pos + 1.2

    # 右侧故障与各层的关联
    failures = list(FAILURE_KB.keys())
    colors_list = ['#ff5252', '#ff8a65', '#4fc3f7', '#81c784']

    # 画故障矩形
    for i, ft in enumerate(failures):
        x_base = 6.5
        y_base = 8.0 - i * 1.8
        color = colors_list[i % len(colors_list)]

        box = FancyBboxPatch((x_base, y_base - 0.5), 5.0, 1.2,
                             boxstyle="round,pad=0.1",
                             facecolor=color + "22", edgecolor=color, linewidth=1.5)
        ax.add_patch(box)
        ax.text(x_base + 2.5, y_base + 0.15, f'⚠️ {ft}',
                ha='center', va='center', fontsize=10, fontweight='bold', color='white')

        # 连接到此故障涉及的各层
        finfo = FAILURE_KB[ft]
        for cause in finfo["possible_causes"]:
            # 映射层名到 y 位置
            layer_y = {
                "L0 通信层": 0,
                "L1 感知层": 1.5,
                "L2 推理层": 3.0,
                "L3 规划层": 4.5,
                "L4 执行层": 6.0,
                "L5 硬件层": 7.5,
            }.get(cause["layer"], 0)
            # 画出关联线
            ax.plot([5.0, x_base], [layer_y + 0.6, y_base],
                    color=color + "44", linewidth=0.5 if cause["probability"] < 0.2 else 1.5,
                    linestyle='-', zorder=1)

    # Layer boxes on the left
    for name, desc, y_pos, color in layers:
        draw_layer_box(y_pos, name, desc, color)

    # 右侧 legend
    ax.text(15, 9.5, '概率权重', fontsize=10, color='#a8b2d1', ha='right')
    ax.plot([14.0, 14.8], [9.0, 9.0], color='white', linewidth=3, label='高概率 (>25%)')
    ax.plot([14.0, 14.8], [8.5, 8.5], color='white', linewidth=0.8, alpha=0.5, label='低概率 (<20%)')
    ax.legend(loc='lower right', fontsize=9, facecolor='#16213e', edgecolor='none')

    plt.tight_layout()
    plt.show()


def visualize_failure_distribution():
    """故障分布对比：各场景的故障模式分布"""
    print("\n" + "=" * 70)
    print("📊 各场景故障模式分布")
    print("=" * 70)

    # 三个场景的故障率分布（模拟数据）
    scene_failures = {
        "仓储 (Warehouse)": {
            "抓取失败": 0.35,
            "定位偏差": 0.20,
            "决策超时": 0.15,
            "碰撞": 0.10,
            "其他": 0.20,
        },
        "制造 (Manufacturing)": {
            "定位偏差": 0.35,
            "抓取失败": 0.25,
            "碰撞": 0.20,
            "决策超时": 0.10,
            "其他": 0.10,
        },
        "农业 (Agriculture)": {
            "抓取失败": 0.30,
            "决策超时": 0.25,
            "定位偏差": 0.20,
            "碰撞": 0.05,
            "其他": 0.20,
        },
    }

    # 对比图
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    colors = ['#ff5252', '#ff8a65', '#4fc3f7', '#81c784', '#a8b2d1']

    for idx, (scene, failures) in enumerate(scene_failures.items()):
        ax = axes[idx]
        labels = list(failures.keys())
        values = list(failures.values())

        bars = ax.barh(labels, values, color=colors[:len(labels)], alpha=0.85, height=0.6)
        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                    f'{val*100:.1f}%', va='center', fontsize=10, color='white')

        ax.set_xlim(0, 0.5)
        ax.set_title(scene, fontsize=12, fontweight='bold')
        ax.set_xlabel('故障率')
        ax.invert_yaxis()

    plt.suptitle('VLA 故障模式分布：仓储 vs 制造 vs 农业', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

    print("\n💡 故障分布分析：")
    print("  - 仓储：抓取失败最多（SKU 多样性）")
    print("  - 制造：定位偏差最多（高精度要求）")
    print("  - 农业：决策超时突出（非结构环境导致推理不确定增加）")
    print("→ 说明 VLA 的故障模式与场景高度相关，兜底策略需要场景定制")


# ============================================================
# Part 4: 五层兜底链模拟
# ============================================================

class FallbackChain:
    """五层兜底链模拟"""

    LAYER_NAMES = {
        0: "L0: 通信层 — 重试+校验",
        1: "L1: 感知层 — 多模态融合+标定",
        2: "L2: 推理层 — 模型降级+超时熔断",
        3: "L3: 规划层 — IK 冗余+碰撞规避",
        4: "L4: 执行层 — 力控+柔顺",
        5: "L5: 硬件层 — 冗余机构+安全急停",
    }

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def simulate_fallback(self, failure_type: str,
                         verbose: bool = True) -> Tuple[int, float, List[str]]:
        """
        模拟故障发生后逐层兜底的过程
        返回 (兜底层级, 总耗时_ms, 各层动作)
        """
        actions = []
        total_time = 0.0

        for layer in range(6):
            # 每层的成功概率
            if layer == 0:
                success_p = 0.30  # 通信重试解决 30%
                time_cost = 50
                action = f"[L{layer}] 通信重试 ×3 → "
            elif layer == 1:
                success_p = 0.40  # 多模态融合
                time_cost = 100
                action = f"[L{layer}] 切换备用视觉 + 重新标定 → "
            elif layer == 2:
                success_p = 0.35  # 模型降级
                time_cost = 200
                action = f"[L{layer}] VLM 降级到轻量模型 + 推理超时熔断 → "
            elif layer == 3:
                success_p = 0.45  # 路径重规划
                time_cost = 80
                action = f"[L{layer}] IK 重求解 + 碰撞规避路径重规划 → "
            elif layer == 4:
                success_p = 0.40  # 柔顺控制
                time_cost = 150
                action = f"[L{layer}] 切换到力控模式 + 柔顺搜索 → "
            else:  # layer 5
                success_p = 0.95  # 硬件冗余
                time_cost = 500
                action = f"[L{layer}] 切换冗余机构 + 急停检查 → "

            total_time += time_cost
            roll = self.rng.random()

            if roll < success_p:
                action += "✅ 兜底成功"
                actions.append(action)
                if verbose:
                    print(f"  {action} (t={total_time:.0f}ms)")
                return layer, total_time, actions
            else:
                action += "❌ 仍失败，继续下一层"
                actions.append(action)
                if verbose:
                    print(f"  {action}")

        # 全部层都失败
        return 5, total_time, actions

    def run_monte_carlo(self, n_simulations: int = 10000) -> Dict:
        """蒙特卡洛模拟各层兜底概率"""
        results = {i: {"count": 0, "times": []} for i in range(6)}
        failed = 0

        for _ in range(n_simulations):
            layer, t, _ = self.simulate_fallback("", verbose=False)
            if layer < 5:
                results[layer]["count"] += 1
                results[layer]["times"].append(t)
            else:
                failed += 1

        return {
            "results": results,
            "failed": failed,
            "total": n_simulations,
        }

    def demo(self):
        """演示五层兜底链"""
        print("\n" + "=" * 70)
        print("🛡️ 五层兜底链模拟")
        print("=" * 70)

        failures = list(FAILURE_KB.keys())
        print(f"\n选择一个故障类型来演示兜底链：")
        for i, ft in enumerate(failures, 1):
            print(f"  {i}. {ft}")
        try:
            choice = int(input(f"\n请选择 [1-{len(failures)}]: ") or "1") - 1
            ft = failures[max(0, min(choice, len(failures) - 1))]
        except:
            ft = failures[0]

        print(f"\n🔍 故障: {ft}")
        print("🛡️ 开始逐层兜底...\n")
        layer, total_t, actions = self.simulate_fallback(ft)

        print(f"\n{'='*70}")
        if layer < 5:
            print(f"✅ 兜底成功！在第 {layer} 层（{self.LAYER_NAMES[layer]}）解决")
        else:
            print(f"❌ 五层兜底均失败！需要人工介入")

        print(f"⏱️ 总耗时: {total_t:.0f}ms ({total_t/1000:.2f}s)")

        # 蒙特卡洛
        print(f"\n📊 蒙特卡洛模拟 (10000 次)...")
        mc = self.run_monte_carlo(10000)
        print(f"\n  各层兜底成功率：")
        print(f"  {'层级':20s} {'成功率':10s} {'均耗时':10s}")
        print(f"  {'-'*40}")
        for l in range(6):
            data = mc["results"][l]
            rate = data["count"] / mc["total"] * 100
            avg_t = np.mean(data["times"]) if data["times"] else 0
            print(f"  {self.LAYER_NAMES[l]:20s} {rate:7.2f}%  {avg_t:8.0f}ms")

        fail_rate = mc["failed"] / mc["total"] * 100
        print(f"  {'完全失败':20s} {fail_rate:7.2f}%")
        print(f"\n💡 面试话术：'五层兜底的核心不是每层都成功，而是每层兜住上一层的漏网之鱼。"
              f"工业场景安全第一——宁可降级运行，不能直接宕机。'")


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🔍 VLA 故障诊断仿真器")
    print("=" * 70)
    print("\n选择演示模式：")
    print("  1 — 交互式 CLI 故障诊断")
    print("  2 — 故障树可视化")
    print("  3 — 故障模式分布对比（各场景）")
    print("  4 — 五层兜底链模拟")
    print("  0 — 全部运行")

    try:
        choice = int(input("\n请输入 (0/1/2/3/4): ") or "0")
    except ValueError:
        choice = 0

    if choice in (0, 1):
        diag = FailureDiagnosis()
        diag.interactive_diagnosis()
    if choice in (0, 2):
        visualize_failure_tree()
    if choice in (0, 3):
        visualize_failure_distribution()
    if choice in (0, 4):
        fc = FallbackChain()
        fc.demo()

    print("\n✅ VLA 故障诊断仿真完成")
    print("💡 面试话术：'故障诊断树 + 五层兜底链是我在面试中一定会画的图——")
    print("   它展示了工业级 VLA 系统不只是模型精度，更是工程体系。'")
