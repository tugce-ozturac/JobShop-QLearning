
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Eğitim sonuçlarını oku
df = pd.read_csv("results/training_history.csv")

# Episode sırasına göre sırala
df = df.sort_values("episode")

# Grafik
plt.figure(figsize=(10, 5))

plt.plot(
    df["episode"],
    df["epsilon"],
    linewidth=2,
    label="Epsilon"
)

plt.title("Epsilon Decay During Training", fontsize=15)
plt.xlabel("Episode")
plt.ylabel("Epsilon Value")
plt.ylim(0, 1.05)
plt.grid(alpha=0.3)
plt.legend()

plt.tight_layout()

# Kaydet
Path("results").mkdir(exist_ok=True)
plt.savefig("results/epsilon_decay.png", dpi=300)
plt.close()

print("Epsilon grafiği oluşturuldu: results/epsilon_decay.png")
