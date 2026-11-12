
import streamlit as st
import pandas as pd

from factory_env import JobShopEnv
from q_learning import QLearningAgent


# ==================================================
# SAYFA AYARLARI
# ==================================================

st.set_page_config(
    page_title="Smart Factory | Q-Learning",
    page_icon="🏭",
    layout="wide"
)

# ==================================================
# TASARIM
# ==================================================

st.markdown("""
<style>
    .stApp {
        background-color: #0e1420;
        color: #e5e7eb;
    }

    [data-testid="stMetric"] {
        background-color: #182235;
        border: 1px solid #29374d;
        padding: 16px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #aab7ca;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff;
    }

    .machine-card {
        background-color: #182235;
        border: 1px solid #29374d;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 10px;
    }

    .machine-title {
        font-size: 21px;
        font-weight: bold;
        color: #ffffff;
    }

    .muted {
        color: #9caec5;
        font-size: 13px;
    }

    .section-title {
        font-size: 21px;
        font-weight: bold;
        color: #f1f5f9;
        margin-top: 12px;
        margin-bottom: 12px;
    }

    .success-text {
        color: #4ade80;
        font-weight: bold;
    }

    .warning-text {
        color: #fbbf24;
        font-weight: bold;
    }

    .danger-text {
        color: #f87171;
        font-weight: bold;
    }

    div.stButton > button {
        border-radius: 9px;
        min-height: 43px;
        font-weight: 600;
    }

    hr {
        border-color: #29374d;
    }
</style>
""", unsafe_allow_html=True)


# ==================================================
# SIMULASYON BASLATMA
# ==================================================

def initialize_simulation():

    env = JobShopEnv()
    state = env.reset()

    agent = QLearningAgent()
    agent.load("results/q_table.pkl")
    agent.epsilon = 0

    st.session_state.env = env
    st.session_state.agent = agent
    st.session_state.state = state

    st.session_state.total_reward = 0
    st.session_state.last_action = "Henüz karar verilmedi"
    st.session_state.last_reward = 0

    st.session_state.step_count = 0
    st.session_state.last_info = {}


if "env" not in st.session_state:

    try:
        initialize_simulation()

    except FileNotFoundError:
        st.error(
            "Q-Tablosu bulunamadı. Önce python train.py komutunu çalıştırın."
        )
        st.stop()


env = st.session_state.env
agent = st.session_state.agent


# ==================================================
# YARDIMCI FONKSIYONLAR
# ==================================================

def action_to_text(action):

    if action == 36:
        return "Bekleme"

    machine_id = action // 12
    job_id = action % 12

    return f"Makine {machine_id + 1} → İş {job_id}"


def get_status(status):

    statuses = {
        "idle": ("🟢", "BOŞ"),
        "busy": ("🔵", "ÜRETİMDE"),
        "broken": ("🔴", "ARIZALI"),
        "setup": ("🟠", "KALIP DEĞİŞİMİ")
    }

    return statuses.get(status, ("⚪", status.upper()))


def get_job_by_id(job_id):

    return next(
        (job for job in env.jobs if job.job_id == job_id),
        None
    )


def advance_simulation(number_of_steps=1):

    for _ in range(number_of_steps):

        if env.done:
            break

        valid_actions = env.get_valid_actions()

        action = agent.choose_action(
            st.session_state.state,
            valid_actions
        )

        next_state, reward, done, info = env.step(action)

        st.session_state.state = next_state

        st.session_state.total_reward += reward
        st.session_state.last_action = action_to_text(action)
        st.session_state.last_reward = reward

        st.session_state.last_info = info
        st.session_state.step_count += 1


# ==================================================
# BASLIK
# ==================================================

st.markdown("""
<div style="padding: 10px 0 18px 0;">
    <div style="font-size:14px;color:#60a5fa;font-weight:bold;">
        REINFORCEMENT LEARNING PROJECT
    </div>
    <div style="font-size:32px;font-weight:800;color:white;">
        🏭 SMART FACTORY
    </div>
    <div style="font-size:15px;color:#94a3b8;">
        Q-Learning Based Dynamic Job-Shop Scheduling System
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()


# ==================================================
# UST METRIKLER
# ==================================================

completed_jobs = [
    job for job in env.jobs
    if job.status == "completed"
]

waiting_jobs = [
    job for job in env.jobs
    if job.status == "waiting"
]

processing_jobs = [
    job for job in env.jobs
    if job.status == "processing"
]

emergency_jobs = [
    job for job in env.jobs
    if job.is_emergency
]

total_jobs = len(env.jobs)

metric1, metric2, metric3, metric4, metric5 = st.columns(5)

metric1.metric(
    "⏱️ Üretim Zamanı",
    env.current_time
)

metric2.metric(
    "📦 Toplam İş",
    total_jobs
)

metric3.metric(
    "✅ Tamamlanan",
    len(completed_jobs)
)

metric4.metric(
    "⌛ Bekleyen",
    len(waiting_jobs)
)

metric5.metric(
    "🏆 Toplam Ödül",
    round(st.session_state.total_reward, 2)
)


st.divider()


# ==================================================
# SIMULASYON KONTROLLERİ
# ==================================================

st.markdown(
    '<div class="section-title">🎮 Simülasyon Kontrol Merkezi</div>',
    unsafe_allow_html=True
)

control1, control2, control3, control4 = st.columns(4)

with control1:

    if st.button(
        "▶ Bir Adım İlerle",
        use_container_width=True,
        disabled=env.done
    ):
        advance_simulation(1)
        st.rerun()


with control2:

    if st.button(
        "⏩ 5 Adım İlerle",
        use_container_width=True,
        disabled=env.done
    ):
        advance_simulation(5)
        st.rerun()


with control3:

    if st.button(
        "🔄 Yeniden Başlat",
        use_container_width=True
    ):
        initialize_simulation()
        st.rerun()


with control4:

    st.markdown("""
    <div style="
        background:#182235;
        border:1px solid #29374d;
        border-radius:9px;
        padding:10px;
        text-align:center;">
        <span style="color:#60a5fa;font-weight:bold;">
            Q-LEARNING AGENT
        </span><br>
        <span style="color:#4ade80;font-size:13px;">
            ● AKTİF
        </span>
    </div>
    """, unsafe_allow_html=True)


if env.done:
    st.success("🎉 Üretim simülasyonu tamamlandı!")


st.divider()


# ==================================================
# MAKINE PANELI
# ==================================================

st.markdown(
    '<div class="section-title">⚙️ Canlı Üretim Hücreleri</div>',
    unsafe_allow_html=True
)

machine_columns = st.columns(3)

for index, machine in enumerate(env.machines):

    with machine_columns[index]:

        icon, status_text = get_status(machine.status)

        st.markdown(
            f"""
            <div class="machine-card">
                <div class="machine-title">
                    ⚙️ MAKİNE {machine.machine_id + 1}
                </div>
                <br>
                <div style="font-size:18px;font-weight:bold;">
                    {icon} {status_text}
                </div>
                <br>
                <div class="muted">
                    Mevcut Kalıp
                </div>
                <div style="font-size:18px;color:white;">
                    {machine.current_mold}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if machine.current_job is not None:

            job = get_job_by_id(machine.current_job)

            st.write(
                f"**Üzerindeki iş:** İş {machine.current_job}"
            )

            if job is not None:

                total_processing = job.processing_times.get(
                    machine.machine_id, 0
                )

                if machine.status == "busy" and total_processing > 0:

                    progress = (
                        total_processing - machine.remaining_time
                    ) / total_processing

                    progress = max(0.0, min(1.0, progress))

                    st.progress(
                        progress,
                        text=f"Üretim ilerlemesi: %{progress * 100:.0f}"
                    )

                elif machine.status == "setup":

                    setup_progress = (
                        env.setup_duration - machine.setup_remaining
                    ) / max(env.setup_duration, 1)

                    setup_progress = max(
                        0.0,
                        min(1.0, setup_progress)
                    )

                    st.progress(
                        setup_progress,
                        text="Kalıp değişimi"
                    )

        else:

            st.write("**Üzerindeki iş:** Yok")

        st.write(
            f"**Kalan süre:** {machine.remaining_time}"
        )

        if machine.status == "broken":

            st.error(
                f"Arıza onarım süresi: {machine.breakdown_remaining}"
            )

        elif machine.status == "idle":

            st.success("Makine yeni iş bekliyor.")

        elif machine.status == "busy":

            st.info("Üretim devam ediyor.")

        elif machine.status == "setup":

            st.warning(
                f"Kalıp değişimi: {machine.setup_remaining}"
            )


st.divider()


# ==================================================
# IS DURUMLARI
# ==================================================

st.markdown(
    '<div class="section-title">📋 İş Takip Merkezi</div>',
    unsafe_allow_html=True
)

job_records = []

for job in env.jobs:

    if job.status == "completed":
        status = "✅ Tamamlandı"

    elif job.status == "processing":
        status = "🔵 Üretimde"

    else:
        status = "⌛ Bekliyor"

    job_records.append({

        "İş No": job.job_id,

        "Kalıp": job.mold_type,

        "Durum": status,

        "Teslim Tarihi": job.due_date,

        "Öncelik": (
            "🚨 ACİL"
            if job.is_emergency
            else "Normal"
        ),

        "Atanan Makine": (
            f"Makine {job.assigned_machine + 1}"
            if job.assigned_machine is not None
            else "-"
        ),

        "Tamamlanma": (
            job.completion_time
            if job.completion_time is not None
            else "-"
        )
    })


job_df = pd.DataFrame(job_records)

st.dataframe(
    job_df,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# IS DURUMU DAGILIMI
# ==================================================

st.markdown(
    '<div class="section-title">📊 Üretim Durumu Özeti</div>',
    unsafe_allow_html=True
)

status1, status2, status3 = st.columns(3)

status1.metric(
    "Bekleyen İşler",
    len(waiting_jobs)
)

status2.metric(
    "Üretimdeki İşler",
    len(processing_jobs)
)

status3.metric(
    "Tamamlanan İşler",
    len(completed_jobs)
)


st.divider()


# ==================================================
# Q-LEARNING KARAR PANELI
# ==================================================

st.markdown(
    '<div class="section-title">🧠 Yapay Zekâ Karar Paneli</div>',
    unsafe_allow_html=True
)

decision1, decision2 = st.columns(2)

with decision1:

    st.info(
        f"**Son seçilen eylem:** {st.session_state.last_action}"
    )

with decision2:

    st.success(
        f"**Son eylemin ödülü:** {st.session_state.last_reward}"
    )


st.write("**Son adım bilgileri**")

if st.session_state.last_info:

    info = st.session_state.last_info

    info1, info2, info3 = st.columns(3)

    info1.metric(
        "Son adım zamanı",
        info.get("time", 0)
    )

    info2.metric(
        "Tamamlanan iş",
        info.get("completed_jobs", 0)
    )

    info3.metric(
        "Bekleyen iş",
        info.get("waiting_jobs", 0)
    )

else:

    st.caption("Henüz bir eylem gerçekleştirilmedi.")


st.divider()


# ==================================================
# EGITIM GRAFIGI
# ==================================================

st.markdown(
    '<div class="section-title">📈 Model Eğitim Performansı</div>',
    unsafe_allow_html=True
)

try:

    st.image(
        "results/training_rewards.png",
        caption="1000 bölüm Q-Learning eğitim ödülleri",
        use_container_width=True
    )

except Exception:

    st.warning("Eğitim grafiği bulunamadı.")


# ==================================================
# ALT BILGI
# ==================================================

st.divider()

st.markdown("""
<div style="text-align:center;color:#64748b;padding:15px;">
    SMART FACTORY | TABULAR Q-LEARNING<br>
    Dynamic Job-Shop Scheduling Simulation
</div>
""", unsafe_allow_html=True)
