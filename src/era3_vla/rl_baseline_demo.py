#!/usr/bin/env python3
"""
rl_demo.py — 强化学习"手感"演示（纯 numpy 版）

让你在 Windows 本机（CPU 即可）感受完整的 RL 训练流程：
  1. 随机策略 → 看看有多菜
  2. 交叉熵方法 (CEM) 训练 → reward 曲线从低往高走
  3. 测试训练好的策略 → 小车学会了！
  4. 可视化对比

不依赖 PyTorch / TensorFlow，只需要 numpy + gymnasium + matplotlib。

用法：
  pip install gymnasium matplotlib numpy
  python src/week_2/rl_demo.py

面试话术：
  "我用 CartPole 跑过 CEM 策略搜索，理解了 RL 的核心循环：
   agent 采样 → 环境反馈 reward → 策略更新 → 收敛。
   虽然简单，但这个循环在机器人 RL 里本质是一样的。"
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import gymnasium as gym


# ============================================================
# 线性策略：CartPole 的观察(4维) → 左/右动作
# 策略 = sign(obs · weights)，weights 是我们需要学的东西
# ============================================================

def evaluate_policy(weights, env, max_steps=500):
    """运行一局游戏，返回总 reward"""
    obs, _ = env.reset()
    total_reward = 0
    for _ in range(max_steps):
        # 线性策略：obs(4,) · weights(4,) → 标量 → sign → 左/右
        action = 0 if np.dot(obs, weights) < 0 else 1
        obs, reward, terminated, truncated, _ = env.step(action)
        total_reward += reward
        if terminated or truncated:
            break
    return total_reward


# ============================================================
# 交叉熵方法 (Cross-Entropy Method, CEM)
#
# 核心思想：
#   1. 生成一批随机策略（权重向量）
#   2. 每个策略跑一局，看 reward
#   3. 挑出最好的那批（elite）
#   4. 用 elite 的均值+方差生成下一批
#   5. 重复 → 策略越来越好
# ============================================================

def train_cem(
    obs_dim=4,
    pop_size=50,      # 每批次生成多少策略
    elite_frac=0.2,   # 挑前 20%
    n_iterations=50,  # 迭代轮数
    seed=42,
):
    """CEM 策略搜索，返回 (best_weights, reward_history)"""
    print("  初始化策略种群 ...")
    rng = np.random.RandomState(seed)

    # 初始均值=0，方差=1
    mean = np.zeros(obs_dim)
    std = np.ones(obs_dim)

    reward_history = []
    best_weights = None
    best_reward = 0

    env = gym.make("CartPole-v1")

    for it in range(n_iterations):
        # Step 1: 从当前分布采样一批策略
        weights_pop = rng.normal(mean, std, size=(pop_size, obs_dim))

        # Step 2: 评估每个策略
        rewards = np.array([evaluate_policy(w, env) for w in weights_pop])

        # Step 3: 选 elite（前 elite_frac）
        n_elite = max(1, int(pop_size * elite_frac))
        elite_idx = np.argsort(rewards)[-n_elite:]
        elite_weights = weights_pop[elite_idx]
        elite_rewards = rewards[elite_idx]

        # Step 4: 用 elite 更新分布
        mean = elite_weights.mean(axis=0)
        std = elite_weights.std(axis=0) + 1e-8  # 加小量防止方差归零

        # 记录
        best_in_gen = rewards.max()
        avg_in_gen = rewards.mean()
        elite_avg = elite_rewards.mean()
        reward_history.append(best_in_gen)

        if best_in_gen > best_reward:
            best_reward = best_in_gen
            best_weights = weights_pop[rewards.argmax()]

        print(f"    第{it+1:2d}代 | 平均={avg_in_gen:5.1f} | 精英平均={elite_avg:5.1f} | 最优={best_in_gen:5.1f}")

        # 如果已经学会（满分 500），提前结束
        if best_in_gen >= 500:
            print(f"    🎉 第{it+1}代就学会了！提前结束")
            break

    env.close()
    return best_weights, reward_history


# ============================================================
# Part 1: 随机策略
# ============================================================

def demo_random_policy(episodes=5):
    """随机策略，看看多菜"""
    print("=" * 55)
    print("  🎲 Part 1: 随机策略 — RL 的起点")
    print("=" * 55)

    env = gym.make("CartPole-v1")
    rewards = []
    for ep in range(episodes):
        obs, _ = env.reset()
        total = 0
        for _ in range(500):
            action = env.action_space.sample()
            obs, r, term, trunc, _ = env.step(action)
            total += r
            if term or trunc:
                break
        rewards.append(total)
        print(f"    第{ep+1}局: reward = {total:.0f}  (满分500)")

    env.close()
    avg = np.mean(rewards)
    print(f"    ─────────────────────────────────────")
    print(f"    📉 随机策略平均: {avg:.1f}/500")
    print(f"    → 纯随机，根本站不稳\n")
    return avg


# ============================================================
# Part 2: CEM 训练
# ============================================================

def run_cem_training():
    """运行 CEM 训练流程"""
    print("=" * 55)
    print("  🧠 Part 2: CEM 策略搜索 — RL 循环实战")
    print("=" * 55)
    print("  算法：交叉熵方法 (Cross-Entropy Method)")
    print("  策略：线性策略 (4维观察 → 左/右动作)")
    print(f"  种群: 50 | 精英率: 20% | 最大代数: 50\n")

    start = time.time()
    best_weights, reward_history = train_cem()
    elapsed = time.time() - start

    print(f"\n  ✅ 训练完成！耗时 {elapsed:.1f} 秒")
    print(f"  最优 reward: {max(reward_history):.0f}/500\n")

    return best_weights, reward_history


# ============================================================
# Part 3: 测试训练好的策略
# ============================================================

def test_trained_policy(weights, episodes=5):
    """测试训练好的策略"""
    print("=" * 55)
    print("  🏆 Part 3: 测试训练好的策略")
    print("=" * 55)

    env = gym.make("CartPole-v1")
    rewards = []
    for ep in range(episodes):
        obs, _ = env.reset()
        total = 0
        for _ in range(500):
            action = 0 if np.dot(obs, weights) < 0 else 1
            obs, r, term, trunc, _ = env.step(action)
            total += r
            if term or trunc:
                break
        rewards.append(total)
        status = "✅ 站到了最后！" if total >= 500 else f"⏱  坚持了 {total:.0f} 步"
        print(f"    第{ep+1}局: reward = {total:.0f}/500  {status}")

    env.close()
    avg = np.mean(rewards)
    print(f"    ─────────────────────────────────────")
    print(f"    📈 训练后平均: {avg:.1f}/500")
    print(f"    {'🎉 学会保持平衡了！' if avg >= 450 else '🔄 有进步，还可以继续训练'}")
    print()
    return avg


# ============================================================
# Part 4: 可视化
# ============================================================

def plot_results(random_avg, reward_history, trained_avg):
    """绘制训练曲线和对比图"""
    print("=" * 55)
    print("  📊 Part 4: 可视化对比")
    print("=" * 55)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    plt.rcParams["axes.unicode_minus"] = False

    # 左图：训练曲线
    ax1 = axes[0]
    generations = np.arange(len(reward_history))
    ax1.plot(generations, reward_history, color="#2196F3", linewidth=1.5, marker="o", markersize=3)
    ax1.axhline(y=500, color="#4CAF50", linestyle="--", alpha=0.5, label="Max=500")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Best Reward")
    ax1.set_title("CEM Training: Best Reward per Generation")
    ax1.legend()
    ax1.grid(alpha=0.3)

    # 右图：随机 vs 训练后
    ax2 = axes[1]
    bars = ax2.bar(
        ["Random", "CEM Trained"],
        [random_avg, trained_avg],
        color=["#EF5350", "#66BB6A"],
        width=0.5,
        edgecolor="white",
        linewidth=1.5,
    )
    for bar, val in zip(bars, [random_avg, trained_avg]):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                 f"{val:.0f}", ha="center", fontsize=12, fontweight="bold")

    ax2.set_ylabel("Avg Reward")
    ax2.set_title("Random vs CEM Trained (CartPole-v1)")
    ax2.set_ylim(0, 550)
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("src/week_2/rl_demo_result.png", dpi=150, bbox_inches="tight")
    print("  ✅ Chart saved: src/week_2/rl_demo_result.png")
    plt.close()  # 不弹窗口（服务器环境）
    print()


# ============================================================
# Part 5: 策略可视化 —— 看看权重的含义
# ============================================================

def explain_weights(weights):
    """解释学到的策略权重含义"""
    print("=" * 55)
    print("  🔬 Part 5: 学到的策略分析")
    print("=" * 55)

    names = ["小车位置", "小车速度", "杆子角度", "杆子角速度"]
    print(f"\n  策略权重: {weights}")
    print()
    for name, w in zip(names, weights):
        direction = "← 左推" if w < 0 else "→ 右推"
        print(f"    {name}: {w:+.3f}  → 观测值越大, 越倾向{direction}")

    print(f"\n  决策规则: 如果 weights · obs < 0 就推左, 否则推右")
    print()


# ============================================================
# 总结
# ============================================================

def print_summary(random_avg, trained_avg):
    print("=" * 55)
    print("  📝 总结：RL 核心四要素")
    print("=" * 55)
    print("""
    ①  Environment (环境): CartPole-v1
        小车+杆子，目标是保持杆子不倒

    ②  Agent (智能体): CEM (Cross-Entropy Method)
        演化策略搜索，简单直观

    ③  Action (动作): 左 / 右 (离散2维)
        每一步选择向左或向右推

    ④  Reward (奖励): 每步+1，倒下则终止
        立得越久 reward 越高\n""")

    improvement = ((trained_avg - random_avg) / max(random_avg, 1)) * 100
    print(f"  🎯 核心结论")
    print(f"     随机策略平均: {random_avg:.0f}/500")
    print(f"     CEM 训练后:   {trained_avg:.0f}/500")
    print(f"     提升:         +{improvement:.0f}%")
    print()
    print(f"  💡 面试话术")
    print(f"     '我用 CartPole 跑过 CEM 策略搜索，理解了 RL 的核心循环：")
    print(f"      agent 采样 → 环境反馈 reward → 策略更新 → 收敛。")
    print(f"      在机器人 RL 中，环境换成 Isaac Sim + Panda 机械臂，")
    print(f"      action 从'左/右'变成 7 个关节角，reward 从'立住'变成'抓取成功'。")
    print(f"      本质是一样的。'\n")
    print("=" * 55)


# ============================================================
# Main
# ============================================================

def main():
    print()
    print("╔" + "═" * 53 + "╗")
    print("║     🤖 强化学习演示 — 从随机到学会平衡（纯 numpy）  ║")
    print("╚" + "═" * 53 + "╝")
    print()

    # Part 1: 随机策略
    random_avg = demo_random_policy(episodes=5)

    # Part 2: CEM 训练
    best_weights, reward_history = run_cem_training()

    # Part 3: 测试训练好的策略
    trained_avg = test_trained_policy(best_weights, episodes=5)

    # Part 4: 可视化
    plot_results(random_avg, reward_history, trained_avg)

    # Part 5: 解释策略
    explain_weights(best_weights)

    # 总结
    print_summary(random_avg, trained_avg)


if __name__ == "__main__":
    main()
