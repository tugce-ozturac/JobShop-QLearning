
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

df = pd.read_csv("results/q_table_summary.csv")

# Q değerlerini sayısal hale getir
df["Q Value"] = pd.to_numeric(df["Q Value"], errors="coerce")
df = df.dropna(subset=["Q Value"])

Path("results").mkdir(exist_ok=True)

# 1. Q Value Distribution
plt.figure(figsize=(10, 5))

plt.hist(
    df["Q Value"],
    bins=40,
    edgecolor="black",
    alpha=0.8
)

plt.title("Q-Value Distribution", fontsize=15)
plt.xlabel("Q Value")
plt.ylabel("Frequency")
plt.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("results/q_value_distribution.png", dpi=300)
plt.close()


# 2. En yüksek Q değerine sahip 15 aksiyon
top_actions = df.nlargest(15, "Q Value").sort_values("Q Value")

plt.figure(figsize=(11, 7))

plt.barh(
    top_actions["Action"],
    top_actions["Q Value"],
    edgecolor="black"
)

plt.title("Top 15 Q-Values", fontsize=15)
plt.xlabel("Q Value")
plt.ylabel("Action")
plt.grid(axis="x", alpha=0.3)

plt.tight_layout()
plt.savefig("results/top_q_values.png", dpi=300)
plt.close()

print("Q-Table grafikleri oluşturuldu!")
print("1. results/q_value_distribution.png")
print("2. results/top_q_values.png")
