
import numpy as np
import random

from factory_env import JobShopEnv
from q_learning import QLearningAgent


def choose_edd_action(env, valid_actions):

    candidates = []

    for action in valid_actions:

        if action == 36:
            continue

        machine_id = action // 12
        job_id = action % 12

        job = next(
            (j for j in env.jobs if j.job_id == job_id),
            None
        )

        machine = env.machines[machine_id]

        if job is None:
            continue

        processing_time = job.processing_times[machine_id]

        setup_time = (
            env.setup_duration
            if machine.current_mold != job.mold_type
            else 0
        )

        candidates.append((
            job.due_date,
            processing_time + setup_time,
            job.job_id,
            machine_id,
            action
        ))

    if not candidates:
        return 36

    # Once teslim tarihi, sonra tahmini islem suresi
    candidates.sort()

    return candidates[0][4]


def run_episode(method, episode_seed, agent=None):

    random.seed(episode_seed)
    np.random.seed(episode_seed)

    env = JobShopEnv()
    state = env.reset()

    done = False
    total_reward = 0

    while not done:

        valid_actions = env.get_valid_actions()

        if method == "Q-Learning":
            action = agent.choose_action(state, valid_actions)
        else:
            action = choose_edd_action(env, valid_actions)

        next_state, reward, done, info = env.step(action)

        state = next_state
        total_reward += reward

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

    return {
        "reward": total_reward,
        "completed": len(completed_jobs),
        "on_time": len(on_time_jobs),
        "tardy": len(tardy_jobs),
        "tardiness": total_tardiness
    }


def evaluate_comparison(episodes=100):

    print("\n========== YONTEM KARSILASTIRMASI ==========")

    agent = QLearningAgent()
    agent.load("results/q_table.pkl")
    agent.epsilon = 0

    results = {
        "Q-Learning": [],
        "EDD": []
    }

    for episode in range(episodes):

        seed = 1000 + episode

        q_result = run_episode(
            "Q-Learning",
            seed,
            agent
        )

        edd_result = run_episode(
            "EDD",
            seed
        )

        results["Q-Learning"].append(q_result)
        results["EDD"].append(edd_result)

    for method, method_results in results.items():

        avg_reward = np.mean([
            r["reward"] for r in method_results
        ])

        avg_completed = np.mean([
            r["completed"] for r in method_results
        ])

        avg_on_time = np.mean([
            r["on_time"] for r in method_results
        ])

        avg_tardy = np.mean([
            r["tardy"] for r in method_results
        ])

        avg_tardiness = np.mean([
            r["tardiness"] for r in method_results
        ])

        total_completed = sum(
            r["completed"] for r in method_results
        )

        total_on_time = sum(
            r["on_time"] for r in method_results
        )

        on_time_rate = (
            total_on_time / total_completed * 100
            if total_completed > 0 else 0
        )

        print(f"\n---------- {method} ----------")
        print("Ortalama odul:", round(avg_reward, 2))
        print("Ortalama tamamlanan is:", round(avg_completed, 2))
        print("Ortalama zamaninda tamamlanan is:", round(avg_on_time, 2))
        print("Ortalama geciken is:", round(avg_tardy, 2))
        print("Ortalama toplam gecikme:", round(avg_tardiness, 2))
        print("Zamaninda teslimat orani:", round(on_time_rate, 2), "%")

    print("\n========== KARSILASTIRMA TAMAMLANDI ==========")


if __name__ == "__main__":
    evaluate_comparison(episodes=100)
