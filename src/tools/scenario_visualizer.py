#!/usr/bin/env python3
"""
scenario_visualizer.py — 面试 PPT 数据可视化工具

功能：
  1. 自动生成面试级图表：三大场景雷达图、对比表、竞争力矩阵
  2. 输出可直接截图插入 PPT 的高质量图形
  3. 生成场景对比表格（终端 Markdown 格式，可粘贴到 PPT）
  4. 1 分钟场景 Pitch 脚本生成

用法：
  pip install numpy matplotlib
  python scenario_visualizer.py

面试话术：「这些图表是我面试时直接用的——雷达图讲场景差异，
            竞争力矩阵讲 智元 的定位，每个图都能引出 2-3 个深度问题。」
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.gridspec as gridspec
from typing import Dict, List, Tuple


# ============================================================
# Part 1: 数据定义
# ============================================================

SCENARIO_DATA = {
    "仓储物流": {
        "color": "#4fc3f7",
        "color_dark": "#0288d1",
        "icon": "📦",
        "specs": {
            "节拍 (s)": 12,
            "精度 (mm)": 5,
            "负载 (kg)": 10,
            "部署密度 (台/千m²)": 8,
            "年运行时长 (h)": 8000,
        },
        "dimensions": {  # 雷达图维度
            "市场规模": 8.5,
            "技术成熟度": 8.0,
            "ROI": 8.5,
            "可复制性": 9.0,
            "竞争壁垒": 5.0,
            "智元适配度": 8.0,
        },
        "vla_advantage": 0.25,  # VLA 相比传统提升
        "key_customer": "京东物流/顺丰",
        "entry_barrier": "中等 — 已有成熟方案",
    },
    "制造装配": {
        "color": "#ff8a65",
        "color_dark": "#d84315",
        "icon": "🔧",
        "specs": {
            "节拍 (s)": 30,
            "精度 (mm)": 0.5,
            "负载 (kg)": 5,
            "部署密度 (台/千m²)": 15,
            "年运行时长 (h)": 6000,
        },
        "dimensions": {
            "市场规模": 9.0,
            "技术成熟度": 6.5,
            "ROI": 7.0,
            "可复制性": 7.0,
            "竞争壁垒": 7.0,
            "智元适配度": 7.5,
        },
        "vla_advantage": 0.15,
        "key_customer": "比亚迪/富士康",
        "entry_barrier": "高 — 精度要求苛刻",
    },
    "农业采摘": {
        "color": "#81c784",
        "color_dark": "#2e7d32",
        "icon": "🌾",
        "specs": {
            "节拍 (s)": 8,
            "精度 (mm)": 15,
            "负载 (kg)": 2,
            "部署密度 (台/千m²)": 3,
            "年运行时长 (h)": 2000,
        },
        "dimensions": {
            "市场规模": 7.0,
            "技术成熟度": 4.5,
            "ROI": 6.5,
            "可复制性": 5.0,
            "竞争壁垒": 8.0,
            "智元适配度": 6.0,
        },
        "vla_advantage": 0.40,
        "key_customer": "大型农场/农业合作社",
        "entry_barrier": "低 — 蓝海市场",
    },
}

# 竞争力矩阵
COMPETITOR_MATRIX = {
    "智元 (AgiBot)": {
        "通用性": 8.0,
        "成本控制": 8.5,
        "场景深度": 6.0,
        "量产能力": 7.0,
        "品牌信任": 5.0,
        "color": "#64ffda",
    },
    "Figure AI": {
        "通用性": 8.5,
        "成本控制": 5.0,
        "场景深度": 7.0,
        "量产能力": 5.0,
        "品牌信任": 7.0,
        "color": "#4fc3f7",
    },
    "特斯拉 Optimus": {
        "通用性": 9.0,
        "成本控制": 6.0,
        "场景深度": 5.0,
        "量产能力": 8.0,
        "品牌信任": 9.0,
        "color": "#ff8a65",
    },
}


# ============================================================
# Part 2: 可视化图表
# ============================================================

def radar_chart(data: Dict, title: str = "三大场景 VLA 适配度雷达图"):
    """画雷达图"""
    categories = list(list(data.values())[0]["dimensions"].keys())
    N = len(categories)

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    for scene_name, scene_data in data.items():
        values = list(scene_data["dimensions"].values())
        values += values[:1]
        ax.fill(angles, values, alpha=0.08, color=scene_data["color"])
        ax.plot(angles, values, 'o-', linewidth=2.5, color=scene_data["color"],
                label=f'{scene_data["icon"]} {scene_name}', markersize=8)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12, color='white')
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=9, color='#a8b2d1')
    ax.tick_params(colors='#a8b2d1', grid_color='#a8b2d133')
    ax.grid(True, alpha=0.3)
    ax.set_title(title, fontsize=15, fontweight='bold', color='#64ffda', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11, facecolor='#16213e',
              edgecolor='none', labelcolor='white')

    plt.tight_layout()
    plt.show()


def competitiveness_matrix():
    """竞争力矩阵气泡图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')

    # 散点图：通用性 vs 场景深度，气泡大小=成本控制
    for name, data in COMPETITOR_MATRIX.items():
        x = data["通用性"]
        y = data["场景深度"]
        size = data["成本控制"] * 200
        ax.scatter(x, y, s=size, c=data["color"], alpha=0.6, edgecolors='white',
                   linewidth=2, zorder=5)
        ax.annotate(name, (x, y), fontsize=12, color='white', fontweight='bold',
                    ha='center', va='center',
                    bbox=dict(facecolor='#16213e', edgecolor='none', alpha=0.7))

    ax.set_xlim(4, 10.5)
    ax.set_ylim(4, 10.5)
    ax.set_xlabel('通用性 (Generalization)', fontsize=12, color='white')
    ax.set_ylabel('场景深度 (Domain Depth)', fontsize=12, color='white')
    ax.set_title('具身智能公司竞争力矩阵', fontsize=15, fontweight='bold', color='#64ffda')
    ax.tick_params(colors='#a8b2d1')
    ax.grid(True, alpha=0.2)

    # 分区注释
    ax.text(5, 9.5, '通用平台型', fontsize=11, color='#a8b2d1', alpha=0.5, ha='center')
    ax.text(9, 5, '场景专精型', fontsize=11, color='#a8b2d1', alpha=0.5, ha='center')
    ax.text(7, 7, '★ 理想位置', fontsize=11, color='#64ffda', alpha=0.5, ha='center')

    plt.tight_layout()
    plt.show()


def comparison_table():
    """生成终端 Markdown 对比表"""
    print("\n" + "=" * 80)
    print("📋 三大场景对比表（可粘贴到 PPT）")
    print("=" * 80)

    headers = ["维度", "仓储物流", "制造装配", "农业采摘"]
    print(f"\n| {' | '.join(headers)} |")
    print(f"|{'|'.join(['---'] * len(headers))}|")

    # 规格对比
    dims = list(list(SCENARIO_DATA.values())[0]["specs"].keys())
    for dim in dims:
        row = [dim]
        for s in SCENARIO_DATA.values():
            row.append(str(s["specs"][dim]))
        print(f"| {' | '.join(row)} |")

    # 场景维度对比
    dims2 = list(list(SCENARIO_DATA.values())[0]["dimensions"].keys())
    for dim in dims2:
        row = [dim]
        for s in SCENARIO_DATA.values():
            row.append(f'{s["dimensions"][dim]:.1f}/10')
        print(f"| {' | '.join(row)} |")

    print(f"\n| {' | '.join(['VLA 增益', f'+{SCENARIO_DATA["仓储物流"]["vla_advantage"]*100:.0f}%',
                           f'+{SCENARIO_DATA["制造装配"]["vla_advantage"]*100:.0f}%',
                           f'+{SCENARIO_DATA["农业采摘"]["vla_advantage"]*100:.0f}%'])} |")
    print(f"| {' | '.join(['目标客户', SCENARIO_DATA["仓储物流"]["key_customer"],
                           SCENARIO_DATA["制造装配"]["key_customer"],
                           SCENARIO_DATA["农业采摘"]["key_customer"]])} |")
    print(f"| {' | '.join(['进入壁垒', SCENARIO_DATA["仓储物流"]["entry_barrier"],
                           SCENARIO_DATA["制造装配"]["entry_barrier"],
                           SCENARIO_DATA["农业采摘"]["entry_barrier"]])} |")


def one_minute_pitch():
    """生成 1 分钟场景 Pitch 脚本"""
    print("\n" + "=" * 80)
    print("🎤 1 分钟场景 Pitch 脚本")
    print("=" * 80)

    pitches = {
        "仓储物流": (
            "「智元的通用机器人在仓储场景，一台替代 3 个工人、三班倒、ROI 1.5 年。"
            "传统 AGV 只能搬，智元机器人能拆垛、拣选、码垛一条龙。"
            "京东物流已经验证了可行性 — 我们下一步是降低 30% 的成本，把 ROI 压到 1 年以内。」"
        ),
        "制造装配": (
            "「3C 精密装配是智元的核心战场。一台替代 2 个高级技工，"
            "VLA 的泛化能力让换线时间从 2 周缩短到 2 天。"
            "我们的混合架构在 ±0.5mm 精度下跑通 95% 良率，"
            "已经达到比亚迪的产线准入标准。」"
        ),
        "农业采摘": (
            "「农业是 VLA 最被低估的场景。传统视觉方案碰到光照变化就崩，"
            "VLA 的泛化能力让采摘成功率从 70% 提升到 90%+。"
            "虽然单体 ROI 不如工业场景，但农业市场规模 3000 亿、"
            "而且几乎没有竞争对手——这是智元的蓝海。」"
        ),
    }

    for scene, pitch in pitches.items():
        print(f"\n📍 {SCENARIO_DATA[scene]['icon']} {scene}:")
        print(f"   {pitch}")


def investment_highlight():
    """投资亮点总结"""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('off')
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')

    highlights = [
        ("市场规模", "三大场景 TAM > ¥5000 亿\n仓储 2000 亿 + 制造 2500 亿 + 农业 500 亿", "#4fc3f7"),
        ("ROI 优势", "仓储 1.5yr / 制造 2.5yr / 农业 3.5yr\n均低于行业平均", "#81c784"),
        ("增长曲线", "2025 渗透率 <5% → 2030 预计 30%+\n年复合增长 >40%", "#ff8a65"),
        ("智元定位", "唯一覆盖三大场景的本土通用机器人\n成本比 Figure 低 40%", "#ffd600"),
    ]

    for i, (title, desc, color) in enumerate(highlights):
        x = i * 3.5 + 0.5
        y = 3

        # 标题
        ax.text(x + 1.5, 5.5, title, ha='center', fontsize=14, fontweight='bold', color=color)
        # 内容
        ax.text(x + 1.5, 3, desc, ha='center', va='center', fontsize=11, color='white')
        # 框
        box = FancyBboxPatch((x, 1.5), 3, 4.5,
                              boxstyle="round,pad=0.1",
                              facecolor=color + "08", edgecolor=color + "44", linewidth=1)
        ax.add_patch(box)

    ax.set_ylim(0, 7)
    ax.set_xlim(0, 14.5)
    ax.text(7, 6.5, '💎 智元投资亮点', ha='center', fontsize=16, fontweight='bold', color='#64ffda')
    plt.show()


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("📊 面试 PPT 数据可视化工具")
    print("=" * 70)
    print("\n选择演示模式：")
    print("  1 — 三大场景雷达图")
    print("  2 — 竞争力矩阵（气泡图）")
    print("  3 — Markdown 对比表")
    print("  4 — 1 分钟 Pitch 脚本")
    print("  5 — 投资亮点总结图")
    print("  0 — 全部运行")

    try:
        choice = int(input("\n请输入 (0/1/2/3/4/5): ") or "0")
    except ValueError:
        choice = 0

    if choice in (0, 1):
        radar_chart(SCENARIO_DATA)
    if choice in (0, 2):
        competitiveness_matrix()
    if choice in (0, 3):
        comparison_table()
    if choice in (0, 4):
        one_minute_pitch()
    if choice in (0, 5):
        investment_highlight()

    print("\n✅ 面试 PPT 可视化工具完成")
    print("💡 面试话术：'这些图表不只是好看——每个点我都能展开讲 3 分钟。")
    print("   比如雷达图里农业的'技术成熟度'最低，但'竞争壁垒'最高——")
    print("   这就是智元可以先发制人的蓝海。'")
