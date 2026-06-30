---
name: workflow-solutions
description: 📄 方案产出 — 3场景方案、ROI分析、上下料方案、龙旗案例
metadata:
  type: reference
---

# 📄 工作流 C：方案产出

> 目标：面试官问场景题时，用三套框架回答 + 张口给 ROI 数据

---

## 📋 总览

| 方案 | 对标 | 核心逻辑 | 你的经验缝合 |
|:---|:---|---:|:---|
| **A 仓储物流** 🏭 | Amazon Vulcan, Agility Digit | SKU多精度低→VLA天然优势 | AGV仓储盘点 |
| **B 制造业** 🔧 | Figure×BMW, Hyundai | 精度高节拍快→兜底设计关键 | 歌尔3C产线 |
| **C 农业/特殊** 🌾 | Lely 奶牛场机器人 | 环境恶劣ROI高→RaaS模式 | 越南交付破局 |
| **上下料专案** 🏭 | 歌尔3C场景切片 | 三级兜底 + VLA混合 | 你最熟的场景 |

---

## 🗂️ 方案文档索引

> 💡 **快速入口 → [`SOLUTION_PORTFOLIO.md`](SOLUTION_PORTFOLIO.md)**（方案作品集完整版）

| 文档 | 大小 | 状态 | 说明 |
|:---|---:|:---:|:---|
| `solution_warehouse.md` | ~17KB | ✅ 完成 | 场景A: 仓储物流深度方案 |
| `solution_manufacturing.md` | ~12KB | ✅ 完成 | 场景B: 制造业深度方案 |
| `solution_agriculture.md` | ~10KB | ✅ 完成 | 场景C: 农业与特殊场景 |
| `solution_loading_unloading.md` | ~13KB | ✅ 完成 | 上下料敲门砖方案 (你最熟) |
| `g2_longcheer_solution.html` | — | ✅ 完成 | 龙旗方案 HTML 可视化 |
| `high_roi_embodied_ai_scenarios.md` | ~8KB | ✅ 完成 | 三大场景 ROI 深度分析 |
| `src/tools/roi_calculator.py` | — | ✅ 完成 | ROI计算器 (可跑) |

---

## 💰 必记 ROI 数据

| 数据 | 值 | 用于哪题 |
|:---|---:|:---:|
| G2 单台 CAPEX | ¥57万 | Q3/Q4/Q6/Q7/Q10/Q12 |
| G2 单台年净现金流 | ¥47.2万/年 | Q3/Q4/Q6/Q7/Q10 |
| G2 单台 IRR | 78.2% | Q6/Q10 |
| G2 单台回收期 | 2.21 年 | Q3/Q6/Q7/Q10/Q12 |
| 4 台产线总投资 | ¥228万 | Q3/Q4/Q10 |
| 4 台年净现金流 | ¥188.8万/年 | Q3/Q4 |
| 4 台静态回收期 | 1.21 年 | Q3/Q4/Q10/Q12 |
| VR 彩盒 IRR | 101% | Q10/Q12 |
| VR 彩盒回收期 | 1.96 年 | Q10/Q12 |
| 龙旗峰值 UPH | 376 | Q4/Q10 |
| 龙旗均值 UPH | 296 | Q4/Q10 |
| 龙旗直通率 | 99.91% | Q4/Q10 |

---

## 🎯 场景识别框架

面试官说一个场景 → 你快速匹配：

```
客户说"我们是3C代工厂"          → 场景B 制造业 (上下料)
客户说"仓库SKU太多"             → 场景A 仓储物流
客户说"农场/偏远/恶劣环境"      → 场景C 农业/特殊
客户说"产线想降本"              → ROI计算器拍数据 → 场景B
```

---

## 🔄 后续待做

| # | 事项 | 优先级 | 时间 |
|:---:|:---|---:|:---:|
| 1 | 三场景方案 + 上下料 + ROI 合并为作品集 | ✅ **已完成** | `SOLUTION_PORTFOLIO.md` |
| 2 | 方案作品集转 PDF/HTML 格式 | 🟡 P1 | 07.14 |
| 3 | 每个方案提炼 1 页"给客户看的"精简版 | 🟡 P1 | 面试前 |
