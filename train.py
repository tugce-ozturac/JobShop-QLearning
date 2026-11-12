
import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from factory_env import JobShopEnv
from q_learning import QLearningAgent


# ==========================================
# EGITIM AYARLARI
# ==========================================

EPISODES = 5000
SEED = 42

os.makedirs("results", exist_ok=True)


def train():

    print("\n========== Q-LEARNING EGITIMI ==========")

    random.seed(SEED)
    np.random.seed(SEED)

    env = JobShopEnv()
    agent = QLearningAgent(
        action_size=37,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.995
    )

    history = []

    for episode in range(1, EPISODES + 1):

        state = env.reset()
        done = False
        total_reward = 0

        while not done:

            # Mevcut durumda yapilabilecek eylemler
            valid_actions = env.get_valid_actions()

            # Ajanin eylem secmesi
            action = agent.choose_action(state, valid_actions)

            # Eylemin fabrikada uygulanmasi
            next_state, reward, done, info = env.step(action)

            # Sonraki durumdaki gecerli eylemler
            if done:
                next_valid_actions = []
            else:
                next_valid_actions = env.get_valid_actions()

            # Q tablosunun guncellenmesi
            agent.update(
                state,
                action,
                reward,
                next_state,
                done,
                next_valid_actions
            )

            state = next_state
            total_reward += reward

        # Her bolum sonunda kesif oranini azalt
        agent.decay_epsilon()

        # Bolum performansini hesapla
        completed_jobs = [
            job for job in env.jobs
            if job.status == "completed"
        ]

        on_time_jobs = [
            job for job in completed_jobs
            if job.completion_time <= job.due_date
        ]

        tardy_jobs = [
            job for job in completed_jobs
            if job.completion_time > job.due_date
        ]

        total_tardiness = sum(
            max(0, job.completion_time - job.due_date)
            for job in completed_jobs
        )

        episode_data = {
            "episode": episode,
            "total_reward": total_reward,
            "completed_jobs": len(completed_jobs),
            "on_time_jobs": len(on_time_jobs),
            "tardy_jobs": len(tardy_jobs),
            "total_tardiness": total_tardiness,
            "epsilon": agent.epsilon,
            "q_table_states": len(agent.q_table)
        }

        history.append(episode_data)

        # Her 100 bolumde ilerlemeyi goster
        if episode % 100 == 0:

            recent_rewards = [
                item["total_reward"]
                for item in history[-100:]
            ]

            average_reward = np.mean(recent_rewards)

            print(
                f"Bolum: {episode}/{EPISODES} | "
                f"Ortalama Odul: {average_reward:.2f} | "
                f"Epsilon: {agent.epsilon:.4f} | "
                f"Q Durum Sayisi: {len(agent.q_table)}"
            )

    # ======================================
    # EGITIM SONUCLARINI KAYDET
    # ======================================

    df = pd.DataFrame(history)

    df.to_csv(
        "results/training_history.csv",
        index=False
    )

    agent.save("results/q_table.pkl")

    # ======================================
    # EGITIM GRAFIGI
    # ======================================

    window = 50

    df["moving_average"] = (
        df["total_reward"]
        .rolling(window=window)
        .mean()
    )

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["episode"],
        df["total_reward"],
        alpha=0.3,
        label="Bolum Odulu"
    )

    plt.plot(
        df["episode"],
        df["moving_average"],
        linewidth=2,
        label="50 Bolumluk Ortalama"
    )

    plt.xlabel("Egitim Bolumu")
    plt.ylabel("Toplam Odul")
    plt.title("Q-Learning Egitim Performansi")
    plt.legend()
    plt.grid(True)

    plt.savefig(
        "results/training_rewards.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # ======================================
    # EGITIM OZETI
    # ======================================

    print("\n========== EGITIM TAMAMLANDI ==========")

    print("Toplam bolum:", EPISODES)
    print("Q tablosundaki durum sayisi:", len(agent.q_table))
    print("Son epsilon:", round(agent.epsilon, 4))

    print("\nSon 100 bolum ortalama odulu:",
          round(df["total_reward"].tail(100).mean(), 2))

    print("\nKaydedilen dosyalar:")
    print("- results/q_table.pkl")
    print("- results/training_history.csv")
    print("- results/training_rewards.png")

    print("=======================================")


if __name__ == "__main__":
    train()
