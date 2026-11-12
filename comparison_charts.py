
import matplotlib.pyplot as plt
import os

os.makedirs("results", exist_ok=True)

methods = ["Q-Learning", "EDD"]

# Deneylerimizden elde edilen sonuçlar
rewards = [273.06, 293.38]
on_time_rates = [60.83, 60.25]
tardiness = [32.29, 12.63]


def create_chart(values, title, ylabel, filename):

    plt.figure(figsize=(8, 5))

    bars = plt.bar(methods, values)

    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel("Scheduling Method")

    plt.grid(axis="y", alpha=0.3)

    for bar, value in zip(bars, values):

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    plt.savefig(
        f"results/{filename}",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()


# 1. Ortalama odul
create_chart(
    rewards,
    "Average Reward Comparison",
    "Average Reward",
    "reward_comparison.png"
)

# 2. Zamaninda teslimat
create_chart(
    on_time_rates,
    "On-Time Delivery Rate Comparison",
    "On-Time Delivery (%)",
    "on_time_comparison.png"
)

# 3. Toplam gecikme
create_chart(
    tardiness,
    "Average Total Tardiness Comparison",
    "Average Tardiness",
    "tardiness_comparison.png"
)

print("\nTum karsilastirma grafikleri kaydedildi!")
