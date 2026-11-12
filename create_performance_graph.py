
import matplotlib.pyplot as plt
from pathlib import Path

# 5000 episode eğitim sonuçları
methods = ["Q-Learning", "EDD"]

metrics = {
    "Average Reward": [303.87, 301.41],
    "On-Time Jobs": [8.1, 7.23],
    "Tardy Jobs": [3.9, 4.77],
    "Total Tardiness": [20.41, 12.63]
}

fig, axes = plt.subplots(2, 2, figsize=(12, 9))

for ax, (title, values) in zip(axes.flat, metrics.items()):
    bars = ax.bar(methods, values, edgecolor="black", width=0.55)

    ax.set_title(title, fontsize=13)
    ax.grid(axis="y", alpha=0.3)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=10
        )

fig.suptitle(
    "Q-Learning vs EDD Performance Comparison",
    fontsize=16
)

plt.tight_layout()

Path("results").mkdir(exist_ok=True)
plt.savefig("results/performance_comparison.png", dpi=300)
plt.close()

print("Performans karşılaştırma grafiği oluşturuldu!")
print("Dosya: results/performance_comparison.png")
