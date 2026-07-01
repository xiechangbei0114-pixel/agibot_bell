#!/usr/bin/env python3
"""
roi_calculator.py — 三大场景 ROI 计算器 + 解决方案仿真

功能：
  1. 交互式 ROI 计算器：输入参数（机器人成本、人工替换比、节拍等），计算投资回报期
  2. 三大场景（仓储/制造/农业）预设对比
  3. 敏感性分析：哪些参数对 ROI 影响最大？
  4. 架构拓扑可视化

用法：
  pip install numpy matplotlib
  python roi_calculator.py

面试话术：「我写了一个 ROI 计算器——客户问'机器人值不值'时，
            不用拍脑袋，直接调参数算 IRR 和回本周期。」
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


# ============================================================
# Part 1: ROI 计算模型
# ============================================================

@dataclass
class RobotSolution:
    """机器人解决方案的成本模型"""

    name: str
    description: str

    # --- 成本参数 ---
    robot_cost: float = 250000       # 单台机器人成本 (元)
    gripper_cost: float = 30000      # 夹爪/末端
    vision_cost: float = 50000       # 视觉系统
    compute_cost: float = 80000      # 计算单元 (工控机 + GPU)
    integration_cost: float = 100000 # 集成部署
    annual_maintenance: float = 30000 # 年维护费
    annual_power: float = 5000       # 年电费
    annual_software: float = 20000   # 年软件许可/VLA 服务
    installation_cost: float = 50000 # 现场安装调试

    # --- 收益参数 ---
    workers_replaced: float = 2      # 替代人工数
    annual_salary_per_worker: float = 100000  # 人均年薪 (元)
    shift_per_day: float = 2         # 每天班次
    uptime: float = 0.95             # 运行率
    quality_improvement: float = 0.02 # 良率提升
    annual_output_value: float = 5000000  # 年产值

    # --- 融资参数 ---
    project_life: int = 5            # 项目周期 (年)
    discount_rate: float = 0.08      # 折现率

    # --- 结果缓存 ---
    _cashflows: List[float] = field(default_factory=list)

    def total_capex(self) -> float:
        """总初始投资"""
        return (self.robot_cost + self.gripper_cost + self.vision_cost
                + self.compute_cost + self.integration_cost + self.installation_cost)

    def annual_opex(self) -> float:
        """年运营成本"""
        return self.annual_maintenance + self.annual_power + self.annual_software

    def annual_benefit(self) -> float:
        """年收益"""
        labor_saved = self.workers_replaced * self.annual_salary_per_worker * self.shift_per_day
        quality_gain = self.annual_output_value * self.quality_improvement
        return labor_saved + quality_gain

    def annual_net_cashflow(self) -> float:
        """年净现金流"""
        return self.annual_benefit() - self.annual_opex()

    def compute_cashflows(self) -> List[float]:
        """计算项目期现金流"""
        cf = [-self.total_capex()]
        for _ in range(self.project_life):
            cf.append(self.annual_net_cashflow())
        self._cashflows = cf
        return cf

    def npv(self) -> float:
        """净现值"""
        cf = self.compute_cashflows()
        return sum(cf[t] / (1 + self.discount_rate) ** t for t in range(len(cf)))

    def irr(self) -> float:
        """内部收益率 (IRR)"""
        cf = self.compute_cashflows()
        # 牛顿法求 IRR
        rate = 0.1
        for _ in range(100):
            npv = sum(cf[t] / (1 + rate) ** t for t in range(len(cf)))
            dnpv = sum(-t * cf[t] / (1 + rate) ** (t + 1) for t in range(1, len(cf)))
            if abs(dnpv) < 1e-6:
                break
            rate_new = rate - npv / dnpv
            if abs(rate_new - rate) < 1e-6:
                break
            rate = rate_new
        return rate

    def payback_period(self) -> Tuple[int, float]:
        """投资回收期 (年)"""
        cf = self.compute_cashflows()
        cumulative = 0
        for t in range(len(cf)):
            cumulative += cf[t]
            if cumulative >= 0:
                # 线性插值
                prev_cum = cumulative - cf[t]
                fraction = -prev_cum / cf[t] if cf[t] != 0 else 0
                return t, fraction
        return self.project_life, 1.0

    def summary(self) -> Dict:
        """完整摘要"""
        years, frac = self.payback_period()
        return {
            "name": self.name,
            "capex": self.total_capex(),
            "opex_per_year": self.annual_opex(),
            "benefit_per_year": self.annual_benefit(),
            "net_cf_per_year": self.annual_net_cashflow(),
            "npv": self.npv(),
            "irr": self.irr(),
            "payback_years": years + frac,
            "project_life": self.project_life,
        }


# ============================================================
# Part 2: 三大场景预设
# ============================================================

SCENE_PRESETS = {
    "G2 × 龙旗 (Longcheer)": RobotSolution(
        name="G2龙旗 — 平板上下料",
        description="智元G2 龙旗南昌工厂 · 平板多媒体测试上下料",
        robot_cost=250000,          # G2 单台成本
        gripper_cost=30000,
        vision_cost=80000,          # 产线视觉定位
        compute_cost=50000,         # 工控+推理
        integration_cost=120000,    # 集成部署+副产线调试
        annual_maintenance=25000,
        annual_software=20000,      # Genie Studio Agent 服务费
        annual_power=5000,
        installation_cost=40000,    # 现场安装+主产线压测
        workers_replaced=3,         # 单台G2替代3名操作工（2班倒）
        annual_salary_per_worker=72000,  # 南昌月薪6000×12
        shift_per_day=2,            # 两班倒
        uptime=0.98,                # 24h连续运转
        quality_improvement=0.015,  # 直通率99.91% (vs 人工~98.5%)
        annual_output_value=6000000, # 单台年处理产值
        project_life=5,
        discount_rate=0.08,
    ),
    "仓储物流 (Warehouse)": RobotSolution(
        name="仓储物流 — 搬运码垛",
        description="Amazon/京东 仓库搬运码垛",
        robot_cost=200000,
        gripper_cost=20000,
        vision_cost=60000,
        compute_cost=60000,
        integration_cost=80000,
        annual_maintenance=25000,
        annual_software=30000,
        workers_replaced=3,       # 一台替代 3 人（24小时）
        annual_salary_per_worker=80000,
        shift_per_day=3,          # 三班倒
        uptime=0.97,
        quality_improvement=0.01,
        annual_output_value=3000000,
        project_life=5,
        discount_rate=0.08,
    ),
    "制造装配 (Manufacturing)": RobotSolution(
        name="制造装配 — 精密装配",
        description="比亚迪/富士康 3C 装配",
        robot_cost=350000,
        gripper_cost=50000,
        vision_cost=100000,
        compute_cost=100000,
        integration_cost=150000,
        annual_maintenance=40000,
        annual_software=30000,
        workers_replaced=2,       # 高精度替代少但价值高
        annual_salary_per_worker=120000,
        shift_per_day=2,
        uptime=0.98,
        quality_improvement=0.05,  # 良率提升显著
        annual_output_value=8000000,
        project_life=5,
        discount_rate=0.10,        # 制造业折现率高
    ),
    "农业采摘 (Agriculture)": RobotSolution(
        name="农业采摘 — 果蔬分拣",
        description="Lely/John Deere 农业采摘",
        robot_cost=300000,
        gripper_cost=40000,
        vision_cost=150000,        # 室外需要更强视觉
        compute_cost=100000,
        integration_cost=120000,
        annual_maintenance=45000,  # 室外环境维护成本高
        annual_software=25000,
        workers_replaced=4,        # 农业劳力密集型
        annual_salary_per_worker=60000,
        shift_per_day=1,           # 白天作业
        uptime=0.85,               # 天气影响
        quality_improvement=0.03,
        annual_output_value=4000000,
        project_life=5,
        discount_rate=0.12,        # 农业风险高
    ),
}


# ============================================================
# Part 3: 可视化
# ============================================================

def run_roi_comparison():
    """三大场景 ROI 对比"""
    print("=" * 70)
    print("💰 ROI 计算器 — 三大场景对比")
    print("=" * 70)

    results = []
    for name, solution in SCENE_PRESETS.items():
        s = solution.summary()
        results.append(s)
        print(f"\n📍 {name}")
        print(f"  {'='*50}")
        print(f"  总投资 (CAPEX):        ¥{s['capex']:>10,.0f}")
        print(f"  年运营成本 (OPEX):     ¥{s['opex_per_year']:>10,.0f}/年")
        print(f"  年收益:                ¥{s['benefit_per_year']:>10,.0f}/年")
        print(f"  年净现金流:            ¥{s['net_cf_per_year']:>10,.0f}/年")
        print(f"  净现值 (NPV):          ¥{s['npv']:>10,.0f}")
        print(f"  内部收益率 (IRR):      {s['irr']*100:>8.1f}%")
        print(f"  投资回收期:            {s['payback_years']:.2f} 年")

    # --- ROI 对比图 ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 左上：CAPEX 构成
    ax = axes[0, 0]
    names = [r["name"].split("—")[0].strip() for r in results]
    capex = [r["capex"] / 10000 for r in results]
    bars = ax.bar(names, capex, color=['#4fc3f7', '#ff8a65', '#81c784'], alpha=0.85)
    for bar, val in zip(bars, capex):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'¥{val:.0f}万', ha='center', fontsize=10)
    ax.set_ylabel('万元', fontsize=11)
    ax.set_title('初始投资 (CAPEX)', fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # 右上：IRR vs 回收期
    ax = axes[0, 1]
    irr = [r["irr"] * 100 for r in results]
    payback = [r["payback_years"] for r in results]
    colors = ['#4fc3f7', '#ff8a65', '#81c784']
    for i in range(len(names)):
        ax.scatter(payback[i], irr[i], c=colors[i], s=200, label=names[i], zorder=5)
        ax.annotate(names[i], (payback[i], irr[i]),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    ax.axhline(15, color='green', linestyle='--', alpha=0.5, label='15% 基准线')
    ax.set_xlabel('投资回收期 (年)', fontsize=11)
    ax.set_ylabel('IRR (%)', fontsize=11)
    ax.set_title('IRR vs 回收期', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    # 左下：年净现金流堆叠
    ax = axes[1, 0]
    x = np.arange(len(names))
    width = 0.35
    benefits = [r["benefit_per_year"] / 10000 for r in results]
    opex = [r["opex_per_year"] / 10000 for r in results]
    net = [b - o for b, o in zip(benefits, opex)]
    ax.bar(x, benefits, width, label='年收益', color='#81c784', alpha=0.7)
    ax.bar(x, opex, width, label='年运营成本', color='#ff5252', alpha=0.7)
    ax.bar(x, net, width, label='年净现金流', color='#4fc3f7', alpha=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9)
    ax.set_ylabel('万元/年', fontsize=11)
    ax.set_title('年现金流分解', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # 右下：NPV 对比
    ax = axes[1, 1]
    npv_vals = [r["npv"] / 10000 for r in results]
    bars = ax.barh(names, npv_vals, color=colors, alpha=0.85)
    for bar, val in zip(bars, npv_vals):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'¥{val:.0f}万', va='center', fontsize=10)
    ax.axvline(0, color='white', linewidth=1)
    ax.set_xlabel('万元', fontsize=11)
    ax.set_title('净现值 NPV (5年)', fontsize=13, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    plt.suptitle('三大场景 ROI 对比分析（GTX 1060 可运行）', fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return results


def sensitivity_analysis():
    """敏感性分析：哪些参数对 ROI 影响最大？"""
    print("\n" + "=" * 70)
    print("📊 敏感性分析 — 哪些参数对 ROI 影响最大？")
    print("=" * 70)

    base = SCENE_PRESETS["制造装配 (Manufacturing)"]
    base_irr = base.irr()

    # 测试参数 ±20%
    params = {
        "机器人成本": ("robot_cost", 0.8, 1.2),
        "替代工人数": ("workers_replaced", 0.8, 1.2),
        "工人年薪": ("annual_salary_per_worker", 0.8, 1.2),
        "良率提升": ("quality_improvement", 0.5, 1.5),
        "年维护费": ("annual_maintenance", 0.8, 1.2),
        "运行率": ("uptime", 0.85, 1.0),
    }

    impacts = []
    fig, ax = plt.subplots(figsize=(12, 6))

    for label, (attr, low_pct, high_pct) in params.items():
        # 低值
        s_low = RobotSolution(**{k: getattr(base, k) for k in RobotSolution.__dataclass_fields__})
        low_val = getattr(base, attr) * low_pct
        setattr(s_low, attr, low_val)
        irr_low = s_low.irr()

        # 高值
        s_high = RobotSolution(**{k: getattr(base, k) for k in RobotSolution.__dataclass_fields__})
        high_val = getattr(base, attr) * high_pct
        setattr(s_high, attr, high_val)
        irr_high = s_high.irr()

        delta_low = (irr_low - base_irr) * 100
        delta_high = (irr_high - base_irr) * 100

        impacts.append((label, delta_low, delta_high))

        print(f"  {label:15s}: {attr:30s} | "
              f"↓{low_pct*100:.0f}%={irr_low*100:.1f}% | "
              f"↑{high_pct*100:.0f}%={irr_high*100:.1f}%")
    # 排序
    impacts.sort(key=lambda x: max(abs(x[1]), abs(x[2])), reverse=True)
    labels = [x[0] for x in impacts]
    lows = [x[1] for x in impacts]
    highs = [x[2] for x in impacts]

    y_pos = np.arange(len(labels))
    ax.barh(y_pos, [abs(min(l, 0)) for l in lows], left=[min(l, 0) for l in lows],
            color='#ff5252', alpha=0.7, label='下降 -20%')
    ax.barh(y_pos, highs, left=0,
            color='#81c784', alpha=0.7, label='上升 +20%')
    ax.axvline(0, color='white', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('IRR 变化 (百分点)', fontsize=11)
    ax.set_title('敏感性分析：各参数 ±20% 对 IRR 的影响', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.show()

    print(f"\n基准 IRR: {base_irr*100:.1f}%")
    print(f"\n💡 敏感性结论：替代工人数和工人年薪是对 ROI 最敏感的参数")
    print("→ 项目谈判时，重点论证能替代多少个工人、工人成本趋势")


def interactive_roi():
    """交互式 ROI 参数调整"""
    print("\n" + "=" * 70)
    print("🔧 交互式 ROI 计算器")
    print("=" * 70)

    print("\n选择预设场景作为起点：")
    scenes = list(SCENE_PRESETS.keys())
    for i, s in enumerate(scenes, 1):
        print(f"  {i}. {s}")
    try:
        choice = int(input(f"\n选择 [1-{len(scenes)}]: ") or "1") - 1
        base_name = scenes[max(0, min(choice, len(scenes) - 1))]
    except:
        base_name = scenes[0]

    sol = SCENE_PRESETS[base_name]
    print(f"\n当前参数 ({base_name}):")
    print(f"  机器人成本: ¥{sol.robot_cost:,.0f}")
    print(f"  替代工人数: {sol.workers_replaced:.0f}")
    print(f"  工人年薪: ¥{sol.annual_salary_per_worker:,.0f}")
    print(f"  良率提升: {sol.quality_improvement*100:.1f}%")

    try:
        ans = input("\n调整参数？(机器人成本/替代工人数/工人年薪, 逗号分隔): ")
        parts = ans.split(",")
        if len(parts) == 3:
            sol.robot_cost = float(parts[0].strip())
            sol.workers_replaced = float(parts[1].strip())
            sol.annual_salary_per_worker = float(parts[2].strip())
    except:
        pass

    s = sol.summary()
    print(f"\n📊 计算结果：")
    print(f"  {'='*50}")
    print(f"  总投资 (CAPEX):     ¥{s['capex']:>10,.0f}")
    print(f"  年净现金流:         ¥{s['net_cf_per_year']:>10,.0f}/年")
    print(f"  净现值 (NPV):       ¥{s['npv']:>10,.0f}")
    print(f"  内部收益率 (IRR):   {s['irr']*100:>7.1f}%")
    print(f"  投资回收期:         {s['payback_years']:.2f} 年")

    if s['irr'] > 0.15:
        print(f"\n✅ IRR > 15%，项目可行！")
    elif s['irr'] > 0.10:
        print(f"\n⚠️ IRR 10-15%，需要进一步优化")
    else:
        print(f"\n❌ IRR < 10%，建议重新评估参数")


def visualize_architecture():
    """场景架构拓扑图"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.patch.set_facecolor('#1a1a2e')

    architectures = {
        "仓储物流": {
            "颜色": "#4fc3f7",
            "节点": ["MES/WMS\n订单下发", "调度系统\n(多机协同)", "VLA 大脑\n路径规划", "移动底盘\n+ 机械臂", "货架/\n传送带"],
            "布局": [(2, 4), (5, 4), (8, 4), (11, 4), (14, 4)],
        },
        "制造装配": {
            "颜色": "#ff8a65",
            "节点": ["MES\n工单下发", "视觉\n定位系统", "VLA\n精密装配", "双机械臂\n协同", "AOI\n质检"],
            "布局": [(2, 4), (5, 5), (8, 4), (11, 3), (14, 5)],
        },
        "农业采摘": {
            "颜色": "#81c784",
            "节点": ["气象/\n生长模型", "视觉感知\n(多光谱)", "VLA\n采摘决策", "柔性臂\n+软夹爪", "分拣\n传送带"],
            "布局": [(2, 4), (5, 5), (8, 4), (11, 3), (14, 4)],
        },
    }

    for idx, (scene, arch) in enumerate(architectures.items()):
        ax = axes[idx]
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 8)
        ax.axis('off')
        ax.set_facecolor('#1a1a2e')
        color = arch["颜色"]

        ax.text(8, 7, scene, ha='center', fontsize=14, fontweight='bold', color=color)

        # 画节点
        for (x, y), label in zip(arch["布局"], arch["节点"]):
            box = FancyBboxPatch((x - 1.2, y - 0.6), 2.4, 1.2,
                                 boxstyle="round,pad=0.08",
                                 facecolor=color + "22", edgecolor=color, linewidth=1.5)
            ax.add_patch(box)
            ax.text(x, y, label, ha='center', va='center',
                    fontsize=8, color='white', fontweight='bold')

        # 画箭头
        for i in range(len(arch["布局"]) - 1):
            x1, y1 = arch["布局"][i]
            x2, y2 = arch["布局"][i + 1]
            ax.annotate('', xy=(x2 - 1.0, y2), xytext=(x1 + 1.0, y1),
                       arrowprops=dict(arrowstyle='->', color=color, lw=2, connectionstyle='arc3,rad=0.1'))

        # 底部说明
        metrics = [
            "节拍: 10-15s/cycle",
            "ROI: 1.5-2.5年",
        ][:2]
        for i, m in enumerate(metrics):
            ax.text(8, 1 - i * 0.5, m, ha='center', fontsize=9, color='#a8b2d1')

    plt.suptitle('三大场景 VLA 解决方案架构拓扑', fontsize=15, fontweight='bold', color='#64ffda')
    plt.tight_layout()
    plt.show()


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("💰 三大场景 ROI 计算器 + 解决方案仿真")
    print("=" * 70)
    print("\n选择演示模式：")
    print("  1 — ROI 对比（三大场景）")
    print("  2 — 敏感性分析")
    print("  3 — 交互式 ROI 计算器")
    print("  4 — 架构拓扑图")
    print("  0 — 全部运行")

    try:
        choice = int(input("\n请输入 (0/1/2/3/4): ") or "0")
    except ValueError:
        choice = 0

    if choice in (0, 1):
        run_roi_comparison()
    if choice in (0, 2):
        sensitivity_analysis()
    if choice in (0, 3):
        interactive_roi()
    if choice in (0, 4):
        visualize_architecture()

    print("\n✅ ROI 计算器仿真完成")
    print("💡 面试话术：'ROI 计算不是数字游戏——替代工人数、工人成本趋势、")
    print("   良率提升是三个最关键参数。客户问'值不值'，你 5 分钟就能调出 IRR。'")
