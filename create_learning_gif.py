
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from pathlib import Path

# Eğitim verilerini oku
df = pd.read_csv("results/training_history.csv")
df = df.sort_values("episode").reset_index(drop=True)

# 100 episode'luk hareketli ortalama
df["moving_average"] = (
    df["total_reward"].rolling(window=100, min_periods=1).mean()
)

# GIF için yaklaşık 100 kare oluştur
step = max(1, len(df) // 100)
frames = list(range(step, len(df) + 1, step))

if len(df) not in frames:
    frames.append(len(df))

# Grafik alanı
fig, ax = plt.subplots(figsize=(10, 6))

ax.set_title("Q-Learning Training Progress", fontsize=16)
ax.set_xlabel("Episode")
ax.set_ylabel("Total Reward")
ax.set_xlim(df["episode"].min(), df["episode"].max())

y_min = min(
    df["total_reward"].min(),
    df["moving_average"].min()
)
y_max = max(
    df["total_reward"].max(),
    df["moving_average"].max()
)
padding = max(1, (y_max - y_min) * 0.1)
ax.set_ylim(y_min - padding, y_max + padding)

ax.grid(True, alpha=0.3)

# Çizgiler
raw_line, = ax.plot(
    [], [], alpha=0.25, linewidth=0.8,
    label="Episode Reward"
)

avg_line, = ax.plot(
    [], [], linewidth=2.5,
    label="100 Episode Moving Average"
)

episode_text = ax.text(
    0.02, 0.95, "",
    transform=ax.transAxes,
    fontsize=11
)

ax.legend(loc="lower right")


def update(frame):
    current = df.iloc[:frame]

    x = current["episode"]

    raw_line.set_data(x, current["total_reward"])
    avg_line.set_data(x, current["moving_average"])

    episode_text.set_text(
        f"Episode: {int(current['episode'].iloc[-1])}"
    )

    return raw_line, avg_line, episode_text


animation = FuncAnimation(
    fig,
    update,
    frames=frames,
    interval=80,
    blit=False
)

# GIF kaydet
Path("results").mkdir(exist_ok=True)

animation.save(
    "results/learning_curve.gif",
    writer=PillowWriter(fps=12)
)

plt.close(fig)

print("GIF başarıyla oluşturuldu!")
print("Dosya: results/learning_curve.gif")
