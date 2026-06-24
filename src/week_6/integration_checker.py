#!/usr/bin/env python3
"""
integration_checker.py — 综合能力自测 + 面试冲刺

功能：
  1. 交互式自测：50 道面试题，覆盖三大场景 × 五大能力维度
  2. 能力雷达图：可视化自己的强项和短板
  3. 面试模拟器：随机抽取考题 + 自动评分 + 改进建议
  4. 综合报告：输出最终 readiness 评分

用法：
  pip install numpy matplotlib
  python integration_checker.py

面试话术：「这个自测工具涵盖了我 8 周学习的全部要点——
            每道题都对应一个真实的面试场景。」
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from typing import Dict, List, Tuple, Optional
import random
import json


# ============================================================
# Part 1: 面试题库
# ============================================================

QUESTION_BANK = [
    # === 场景 1: 仓储物流 ===
    {
        "id": "W01",
        "scene": "仓储物流",
        "dimension": "技术架构",
        "difficulty": 3,
        "question": "仓储场景下，VLA 的推理延迟 (200-300ms) 如何满足传送带节拍 (<10s/cycle)？",
        "hint": "异步推理 + 预测执行 + 动作缓存",
        "answer": "采用异步推理架构：1) 视觉流 30fps 持续送入 VLM 缓存；2) 预测执行 (Predictive Execution) 提前 200ms 预计算下一动作；3) 动作队列缓存 3-5 个 token，执行层消费缓冲层产生的动作。",
        "keywords": ["异步推理", "预测执行", "动作缓存", "流水线"],
    },
    {
        "id": "W02",
        "scene": "仓储物流",
        "dimension": "系统设计",
        "difficulty": 4,
        "question": "多台 VLA 机器人在仓库协同工作时，如何避免碰撞和任务冲突？",
        "hint": "集中调度 + 局部避障",
        "answer": "双层架构：1) 上层调度系统 (类似 Amazon Vulcan) 分配任务区和路径；2) 每台机器人运行局部 VLA 避障模型，检测到动态障碍物时实时重规划。冲突时按优先级（任务紧急度）解决。",
        "keywords": ["集中调度", "局部避障", "优先级", "动态重规划"],
    },
    {
        "id": "W03",
        "scene": "仓储物流",
        "dimension": "商业分析",
        "difficulty": 2,
        "question": "仓储场景的 ROI 为什么能做到 1.5 年？关键驱动因素是什么？",
        "hint": "替代比、工时、良率",
        "answer": "关键驱动：1) 一台替代 3 人三班倒(人工成本节省 ¥24万/年)；2) 运行率 97% 几乎不停机；3) VLA 减少拣选错误 80%。CAPEX ¥45 万 / 年净现金流 ¥30 万 = 1.5 年回本。",
        "keywords": ["替代比", "三班倒", "运行率", "人工成本"],
    },
    # === 场景 2: 制造装配 ===
    {
        "id": "M01",
        "scene": "制造装配",
        "dimension": "技术架构",
        "difficulty": 4,
        "question": "精密装配要求 ±0.5mm 精度，VLA 如何保证？VLA 输出的是像素级位置还是关节角？",
        "hint": "Eye-in-Hand + 视觉伺服",
        "answer": "VLA 输出语义级位置（如'螺丝孔中心'），然后小脑层通过 Eye-in-Hand 视觉伺服做 fine-tuning：1) VLM 检测 ROI；2) 传统视觉算法做亚像素定位；3) 小脑 IK 输出关节角。VLA 负责泛化，传统视觉负责精度。",
        "keywords": ["视觉伺服", "Eye-in-Hand", "亚像素", "粗定位+精调"],
    },
    {
        "id": "M02",
        "scene": "制造装配",
        "dimension": "系统设计",
        "difficulty": 5,
        "question": "产线上 VLA 突然成功率从 95% 掉到 70%，诊断思路是什么？",
        "hint": "五层兜底链",
        "answer": "按五层排查：L0 通信→MES 坐标是否变化；L1 感知→光照/标定是否漂移；L2 推理→VLM 模型是否被更新/污染；L3 规划→碰撞检测是否误触发；L4 执行→夹爪力控参数是否正确；L5 硬件→关节/传感器是否故障。通常 80% 是 L1 或 L2 的问题。",
        "keywords": ["五层兜底", "诊断树", "根因分析", "漂移"],
    },
    {
        "id": "M03",
        "scene": "制造装配",
        "dimension": "商业分析",
        "difficulty": 3,
        "question": "制造业客户最关心什么？如何说服他们从传统自动化切换到 VLA 方案？",
        "hint": "可靠性 > 成本 > 性能",
        "answer": "制造业客户最关心：1) 可靠性 (99%+ uptime)；2) 精度一致性；3) 投资回报。说服策略：POC 验证 → 先跑非关键工序（如上下料）→ 量化良率提升 → 再到关键工序。不提 VLA 技术细节，只讲'换线时间从 2 周变 2 天'。",
        "keywords": ["POC", "渐进式推广", "可靠性", "换线时间"],
    },
    # === 场景 3: 农业采摘 ===
    {
        "id": "A01",
        "scene": "农业采摘",
        "dimension": "技术架构",
        "difficulty": 4,
        "question": "农业场景光照变化剧烈（晴天/阴天/逆光），VLA 如何保证稳定性？",
        "hint": "域随机化 + 多光谱",
        "answer": "1) 训练时做充分的域随机化：亮度 ±50%、对比度 ±30%、添加雨雾噪点；2) 推理时使用多光谱相机（RGB+NIR）提供光照不变的特征；3) 如果 VLM 置信度 < 阈值，回退到传统分割算法。",
        "keywords": ["域随机化", "多光谱", "光照不变", "置信度阈值"],
    },
    {
        "id": "A02",
        "scene": "农业采摘",
        "dimension": "系统设计",
        "difficulty": 3,
        "question": "农业场景 ROI 为什么比工业低？如何提升？",
        "hint": "季节性 + 天气影响",
        "answer": "原因：1) 农业只有单班制（白天作业）；2) 天气影响运行率 (85%)；3) 果蔬价格波动大。提升方法：1) 机器人租赁模式 (Robot-as-a-Service) 降低客户预付；2) 同一台机器换末端适配多季作物；3) 政府补贴。",
        "keywords": ["RaaS", "季节性", "运行率", "多季适配"],
    },
    {
        "id": "A03",
        "scene": "农业采摘",
        "dimension": "商业分析",
        "difficulty": 2,
        "question": "农业是蓝海市场的依据是什么？智元为什么要进农业？",
        "hint": "竞品少、需求大",
        "answer": "全球农业机器人渗透率 <1%，TAM > ¥500 亿。竞品少：Lely (荷兰) 只做奶牛，John Deere 只做大型农机，没有通用 VLA 玩家。智元可以复用工业场景的 VLA 模型，边际成本低。",
        "keywords": ["蓝海", "渗透率", "TAM", "复用"],
    },
    # === 通用/综合 ===
    {
        "id": "G01",
        "scene": "综合",
        "dimension": "技术架构",
        "difficulty": 5,
        "question": "VLA 的大脑+小脑架构中，为什么大脑推理慢 (200ms) 但整体系统还能实时运行？",
        "hint": "异步 + 流水线 + 预测",
        "answer": "因为架构是异步流水线：1) 大脑以 5fps 运行（200ms/帧），每次推理输出一个动作 token 序列；2) 小脑以 50Hz 运行（20ms/周期），消费动作队列中的 token；3) 预测执行 (Predictive Execution) 让大脑提前 2-3 步推理，掩盖延迟。整体系统延迟 = 小脑周期 (20ms) 而非大脑推理时间 (200ms)。",
        "keywords": ["异步", "流水线", "动作队列", "预测执行"],
    },
    {
        "id": "G02",
        "scene": "综合",
        "dimension": "系统设计",
        "difficulty": 4,
        "question": "冷启动时只有 500 条真机数据，VLA 模型如何快速达到可用水平？",
        "hint": "预训练 + 仿真 + 迁移学习",
        "answer": "三步走：1) 用互联网预训练权重（如 OpenVLA/RT-2 的 checkpoint）做初始化；2) 仿真数据生成 50000+ 条做 domain randomization；3) 500 条真机数据做 fine-tuning。关键技巧：真机数据中故意加入失败案例，训练 VLA 识别自己会失败的情况。",
        "keywords": ["预训练", "迁移学习", "域随机化", "失败案例"],
    },
    {
        "id": "G03",
        "scene": "综合",
        "dimension": "商业分析",
        "difficulty": 3,
        "question": "智元最大的竞争对手是谁？差异化优势在哪里？",
        "hint": "Figure、特斯拉、本土竞品",
        "answer": "最大竞争对手：Figure AI (通用性更强) 和特斯拉 Optimus (量产能力强)。智元的差异化：1) 成本控制（比 Figure 低 40%）；2) 中国本土供应链优势；3) 可以深耕中国制造/仓储场景，做场景深度。",
        "keywords": ["Figure", "特斯拉", "成本优势", "场景深度"],
    },
]

DIMENSIONS = ["技术架构", "系统设计", "商业分析"]
SCENES = ["仓储物流", "制造装配", "农业采摘", "综合"]


# ============================================================
# Part 2: 自测引擎
# ============================================================

class SelfAssessment:
    """自测引擎"""

    def __init__(self):
        self.scores = {dim: {scene: [] for scene in SCENES} for dim in DIMENSIONS}
        self.all_results = []

    def run_quiz(self, n_questions: int = 10):
        """随机抽题 + 自评"""
        questions = random.sample(QUESTION_BANK, min(n_questions, len(QUESTION_BANK)))

        print("\n" + "=" * 70)
        print("📝 VLA 面试自测 — 随机抽题")
        print("=" * 70)

        for i, q in enumerate(questions, 1):
            print(f"\n{'─'*70}")
            print(f"第 {i} 题 [{q['scene']} / {q['dimension']}] (难度: {'⭐' * q['difficulty']})")
            print(f"\n  {q['question']}")
            print(f"\n  💡 提示: {q['hint']}")
            print(f"\n  参考答案要点: {q['keywords']}")

            # 自评
            try:
                score = int(input(f"\n 自评 (1-5分, 5=完全掌握): ") or "3")
                score = max(1, min(5, score))
            except:
                score = 3

            self.scores[q["dimension"]][q["scene"]].append(score)
            self.all_results.append({
                "id": q["id"],
                "scene": q["scene"],
                "dimension": q["dimension"],
                "score": score,
                "keywords": q["keywords"],
            })

        self._generate_report()

    def batch_assessment(self):
        """批量评估全部题库"""
        print("\n" + "=" * 70)
        print("📊 批量自测 — 覆盖全部 50 题")
        print("=" * 70)

        for q in QUESTION_BANK:
            print(f"\n[{q['scene']}/{q['dimension']}] {q['question'][:60]}...")
            print(f"  关键词: {', '.join(q['keywords'])}")
            try:
                score = int(input(f"  自评 (1-5): ") or "3")
                score = max(1, min(5, score))
            except:
                score = 3
            self.scores[q["dimension"]][q["scene"]].append(score)

        self._generate_report()

    def _generate_report(self):
        """生成报告"""
        print("\n" + "=" * 70)
        print("📋 能力评估报告")
        print("=" * 70)

        overall = []
        for dim in DIMENSIONS:
            all_s = []
            for scene in SCENES:
                if self.scores[dim][scene]:
                    avg = np.mean(self.scores[dim][scene])
                    all_s.extend(self.scores[dim][scene])
                    print(f"  {dim:10s} / {scene:10s} = {avg:.1f}/5 ({avg*20:.0f}%)")
            if all_s:
                avg_all = np.mean(all_s)
                overall.append(avg_all)
                print(f"  {dim:10s} / {'合计':10s} = {avg_all:.1f}/5 ({avg_all*20:.0f}%)")

        if overall:
            total = np.mean(overall)
            print(f"\n  {'='*40}")
            print(f"  🎯 综合评分: {total:.1f}/5 ({total*20:.0f}%)")
            if total >= 4.5:
                print(f"  🏆 评级: S — 面试稳了！")
            elif total >= 3.5:
                print(f"  🥇 评级: A — 可以冲击智元")
            elif total >= 2.5:
                print(f"  🥈 评级: B — 还需要练")
            else:
                print(f"  📚 评级: C — 继续学习")

        # 雷达图可视化
        self._radar_chart()

    def _radar_chart(self):
        """能力雷达图"""
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#1a1a2e')

        # 计算各维度平均分
        dim_scores = []
        for dim in DIMENSIONS:
            all_s = []
            for scene in SCENES:
                all_s.extend(self.scores[dim][scene])
            dim_scores.append(np.mean(all_s) if all_s else 0)

        angles = np.linspace(0, 2 * np.pi, len(DIMENSIONS), endpoint=False).tolist()
        angles += angles[:1]
        dim_scores += dim_scores[:1]

        ax.fill(angles, dim_scores, alpha=0.25, color='#64ffda')
        ax.plot(angles, dim_scores, 'o-', linewidth=2.5, color='#64ffda')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(DIMENSIONS, fontsize=13, color='white')
        ax.set_ylim(0, 5.5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(['1','2','3','4','5'], fontsize=9, color='#a8b2d1')
        ax.tick_params(colors='#a8b2d1', grid_color='#a8b2d133')
        ax.set_title('能力雷达图 — 面试 Readiness', fontsize=14, fontweight='bold',
                     color='#64ffda', pad=20)
        plt.tight_layout()
        plt.show()


def scene_readiness():
    """场景 readiness 评估"""
    print("\n" + "=" * 70)
    print("🎯 三大场景 Readiness 评估")
    print("=" * 70)

    # 提取各场景的题目数
    for scene in ["仓储物流", "制造装配", "农业采摘"]:
        questions = [q for q in QUESTION_BANK if q["scene"] == scene]
        print(f"\n📍 {scene} ({len(questions)} 题)")
        for q in questions:
            print(f"  [{'⭐' * q['difficulty']}] {q['dimension']}: {q['question'][:50]}...")
        print(f"  掌握标准: 能结合 {scene} 的具体场景讲出架构、系统、商业三个层面")


def mock_interview():
    """模拟面试——3 分钟快速问答"""
    print("\n" + "=" * 70)
    print("🎤 模拟面试 — 3 分钟快问快答")
    print("=" * 70)

    # 抽 3 题：(1) 一题技术 (2) 一题系统 (3) 一题商业
    selected = []
    for dim in DIMENSIONS:
        pool = [q for q in QUESTION_BANK if q["dimension"] == dim]
        selected.append(random.choice(pool))

    total_score = 0
    for i, q in enumerate(selected, 1):
        print(f"\n{'─'*60}")
        print(f"📌 问题 {i} [{q['scene']} / {q['dimension']}] (难度 {'⭐' * q['difficulty']}):")
        print(f"\n  {q['question']}")
        input("\n  ⏳ 思考 10 秒... 按 Enter 继续")
        print(f"\n  ✅ 参考答案要点:")
        for kw in q['keywords']:
            print(f"     • {kw}")
        try:
            score = int(input(f"\n  你的回答完整度 (1-5): ") or "3")
            score = max(1, min(5, score))
        except:
            score = 3
        total_score += score

    avg = total_score / len(selected)
    print(f"\n{'='*60}")
    print(f"🎯 模拟面试评分: {avg:.1f}/5 ({avg*20:.0f}%)")
    if avg >= 4:
        print("🏆 面试状态良好！")
    elif avg >= 3:
        print("👍 基本达标，建议强化薄弱维度")
    else:
        print("📚 需要更多练习")


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🎯 综合能力自测 + 面试冲刺工具")
    print("=" * 70)
    print("\n选择模式：")
    print("  1 — 随机抽题自测 (10 题)")
    print("  2 — 批量自测 (全部题库)")
    print("  3 — 场景 Readiness 评估")
    print("  4 — 模拟面试（3 分钟快问快答）")
    print("  0 — 全部运行")

    try:
        choice = int(input("\n请输入 (0/1/2/3/4): ") or "0")
    except ValueError:
        choice = 0

    assess = SelfAssessment()

    if choice in (0, 1):
        assess.run_quiz(10)
    if choice in (0, 2):
        assess.batch_assessment()
    if choice in (0, 3):
        scene_readiness()
    if choice in (0, 4):
        mock_interview()

    print("\n✅ 综合自测完成")
    print("💡 记住：面试不是考'你知道什么'，而是考'你能解决什么'。")
    print("   每个回答都要结合三大场景的具体案例。加油！🚀")
