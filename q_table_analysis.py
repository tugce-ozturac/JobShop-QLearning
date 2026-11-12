
import pandas as pd
import numpy as np

from q_learning import QLearningAgent


def analyze_q_table():

    agent = QLearningAgent()
    agent.load("results/q_table.pkl")

    q_table = agent.q_table

    print("\n========== Q-TABLOSU ANALIZI ==========")

    print("Toplam durum sayisi:", len(q_table))

    records = []

    for state, q_values in q_table.items():

        for action, q_value in enumerate(q_values):

            # Sadece sifirdan farkli Q degerlerini incele
            if q_value != 0:

                if action == 36:
                    machine_name = "Bekleme"
                    job_id = "-"
                    action_name = "Bekle"

                else:
                    machine_id = action // 12
                    job_id = action % 12

                    machine_name = f"Makine {machine_id + 1}"
                    action_name = (
                        f"{machine_name} -> Is {job_id}"
                    )

                records.append({
                    "State": str(state),
                    "Action ID": action,
                    "Action": action_name,
                    "Q Value": round(float(q_value), 4)
                })

    if not records:
        print("Tabloda sifirdan farkli Q degeri bulunamadi.")
        return

    df = pd.DataFrame(records)

    # En yuksek Q degerlerini sirala
    df = df.sort_values(
        by="Q Value",
        ascending=False
    )

    print("\nOgrenilmis eylem sayisi:", len(df))

    print("\nEn yuksek 15 Q degeri:")
    print(df.head(15).to_string(index=False))

    # CSV olarak kaydet
    df.to_csv(
        "results/q_table_summary.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nQ tablosu analizi kaydedildi:")
    print("results/q_table_summary.csv")

    print("\n========== ANALIZ TAMAMLANDI ==========")


if __name__ == "__main__":
    analyze_q_table()
