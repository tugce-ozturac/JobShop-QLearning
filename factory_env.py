
from dataclasses import dataclass
from typing import Dict, List, Optional
import random


# ==========================================
# 1. İŞ SINIFI
# ==========================================

@dataclass
class Job:

    job_id: int
    mold_type: str
    processing_times: Dict[int, int]
    due_date: int

    priority: int = 1
    status: str = "waiting"

    assigned_machine: Optional[int] = None
    remaining_time: int = 0
    completion_time: Optional[int] = None
    arrival_time: int = 0

    @property
    def is_emergency(self):
        return self.priority == 2


# ==========================================
# 2. MAKİNE SINIFI
# ==========================================

@dataclass
class Machine:

    machine_id: int
    compatible_molds: List[str]
    current_mold: str

    status: str = "idle"

    current_job: Optional[int] = None
    remaining_time: int = 0

    setup_remaining: int = 0
    breakdown_remaining: int = 0

    total_work_time: int = 0
    total_idle_time: int = 0
    total_setup_time: int = 0
    total_breakdown_time: int = 0


# ==========================================
# 3. JOB-SHOP ORTAMI
# ==========================================

class JobShopEnv:

    def __init__(self):

        self.machines = []
        self.jobs = []

        self.current_time = 0

        self.setup_duration = 2
        self.breakdown_duration = 3

        self.done = False

        self.reset()

    # ======================================
    # ORTAMI SIFIRLAMA
    # ======================================

    def reset(self):

        self.current_time = 0
        self.done = False

        self.emergency_added = False
        self.broken_once = set()

        # Makinelerin oluşturulması

        self.machines = [

            Machine(0, ["K1", "K2"], "K1"),

            Machine(1, ["K1", "K2", "K3"], "K2"),

            Machine(2, ["K2", "K3"], "K3")

        ]

        # Başlangıç işleri

        self.jobs = [

            Job(0, "K1", {0: 4, 1: 5}, 12),
            Job(1, "K2", {0: 5, 1: 4, 2: 6}, 15),
            Job(2, "K3", {1: 6, 2: 4}, 18),
            Job(3, "K1", {0: 3, 1: 5}, 10),
            Job(4, "K2", {0: 6, 1: 3, 2: 5}, 20),
            Job(5, "K3", {1: 4, 2: 5}, 16),
            Job(6, "K1", {0: 5, 1: 4}, 22),
            Job(7, "K2", {0: 4, 1: 6, 2: 3}, 14),
            Job(8, "K3", {1: 5, 2: 3}, 19),
            Job(9, "K1", {0: 6, 1: 3}, 17),
            Job(10, "K2", {0: 3, 1: 5, 2: 4}, 24)

        ]

        return self.get_state()

    # ======================================
    # BEKLEYEN İŞLER
    # ======================================

    def get_waiting_jobs(self):

        return [

            job for job in self.jobs

            if job.status == "waiting"

        ]

    # ======================================
    # MAKİNEYE UYGUN İŞLER
    # ======================================

    def get_available_jobs(self, machine_id):

        available_jobs = []

        machine = self.machines[machine_id]

        if machine.status != "idle":
            return available_jobs

        for job in self.jobs:

            if job.status != "waiting":
                continue

            if machine_id not in job.processing_times:
                continue

            if job.mold_type not in machine.compatible_molds:
                continue

            available_jobs.append(job)

        return available_jobs

    # ======================================
    # İŞE UYGUN MAKİNELER
    # ======================================

    def get_compatible_machines(self, job_id):

        job = self.jobs[job_id]

        compatible_machines = []

        for machine in self.machines:

            if machine.machine_id not in job.processing_times:
                continue

            if job.mold_type not in machine.compatible_molds:
                continue

            compatible_machines.append(machine)

        return compatible_machines

    # ======================================
    # MAKİNEYE İŞ ATAMA
    # ======================================

    def assign_job(self, machine_id, job_id):

        machine = self.machines[machine_id]
        job = self.jobs[job_id]

        if machine.status != "idle":
            return False

        if job.status != "waiting":
            return False

        if machine_id not in job.processing_times:
            return False

        if job.mold_type not in machine.compatible_molds:
            return False

        machine.current_job = job_id

        job.assigned_machine = machine_id
        job.status = "assigned"

        if machine.current_mold != job.mold_type:

            machine.status = "setup"

            machine.setup_remaining = self.setup_duration

            machine.total_setup_time += self.setup_duration

        else:

            machine.status = "busy"

            machine.remaining_time = job.processing_times[machine_id]

            job.remaining_time = machine.remaining_time

            job.status = "processing"

        return True

    # ======================================
    # ÜRETİMİ BAŞLATMA
    # ======================================

    def start_production(self, machine):

        job = self.jobs[machine.current_job]

        machine.current_mold = job.mold_type

        machine.remaining_time = job.processing_times[
            machine.machine_id
        ]

        job.remaining_time = machine.remaining_time

        job.status = "processing"

        machine.status = "busy"

    # ======================================
    # MAKİNE ARIZASI
    # ======================================

    def trigger_breakdown(self, machine_id):

        machine = self.machines[machine_id]

        if machine.status not in ["idle", "busy"]:
            return False

        machine.status = "broken"

        machine.breakdown_remaining = self.breakdown_duration

        return True

    # ======================================
    # ACİL SİPARİŞ EKLEME
    # ======================================

    def add_emergency_job(self):

        if self.emergency_added:
            return False

        new_job = Job(

            job_id=len(self.jobs),

            mold_type="K2",

            processing_times={
                0: 3,
                1: 2,
                2: 4
            },

            due_date=self.current_time + 7,

            priority=2,

            status="waiting",

            arrival_time=self.current_time

        )

        self.jobs.append(new_job)

        self.emergency_added = True

        print(
            f"ACIL SIPARIS GELDI! "
            f"Is No: {new_job.job_id}"
        )

        return True

    # ======================================
    # MAKİNE DURUMLARINI GÜNCELLEME
    # ======================================

    def update_machines(self):

        for machine in self.machines:

            if machine.status == "setup":

                machine.setup_remaining -= 1

                if machine.setup_remaining <= 0:

                    self.start_production(machine)

            elif machine.status == "busy":

                machine.remaining_time -= 1

                machine.total_work_time += 1

                job = self.jobs[machine.current_job]

                job.remaining_time = machine.remaining_time

                if machine.remaining_time <= 0:

                    job.status = "completed"

                    job.completion_time = self.current_time + 1

                    machine.current_job = None

                    machine.status = "idle"

                    machine.remaining_time = 0

                    print(
                        f"Is {job.job_id} tamamlandi! "
                        f"Makine {machine.machine_id + 1}"
                    )

            elif machine.status == "broken":

                machine.breakdown_remaining -= 1

                machine.total_breakdown_time += 1

                if machine.breakdown_remaining <= 0:

                    if machine.current_job is not None:

                        machine.status = "busy"

                    else:

                        machine.status = "idle"

                    print(
                        f"Makine {machine.machine_id + 1} "
                        f"bakimdan cikti."
                    )

            elif machine.status == "idle":

                machine.total_idle_time += 1

    # ======================================
    # ZAMAN İLERLETME
    # ======================================

    def step_time(self):

        if self.done:
            return

        self.update_machines()

        self.current_time += 1

        if self.current_time >= 35:

            self.done = True

   
    # ======================================
    # STATE OLUŞTURMA
    # ======================================

    def get_state(self):

        machine_states = []

        status_map = {
            "idle": 0,
            "busy": 1,
            "broken": 2,
            "setup": 3
        }

        mold_map = {
            "K1": 0,
            "K2": 1,
            "K3": 2
        }

        # 1. MAKİNE DURUMLARI

        for machine in self.machines:

            machine_states.extend([

                status_map[machine.status],

                mold_map[machine.current_mold],

                (machine.current_job + 1)
                if machine.current_job is not None else 0,

                min(machine.remaining_time, 10),

                min(machine.setup_remaining, 5),

                min(machine.breakdown_remaining, 5)

            ])

        # 2. İŞ DURUMLARI

        waiting_mask = 0
        completed_mask = 0
        urgent_mask = 0

        for job in self.jobs:

            bit = 1 << job.job_id

            if job.status == "waiting":

                waiting_mask |= bit

            if job.status == "completed":

                completed_mask |= bit

            if job.status not in ["completed", "cancelled"]:

                remaining_due = job.due_date - self.current_time

                if remaining_due <= 3:

                    urgent_mask |= bit

        # 3. HER İŞİN KALAN TESLİM SÜRESİ

        deadline_states = []

        MAX_JOBS = 12

        job_dict = {
            job.job_id: job
            for job in self.jobs
        }

        for job_id in range(MAX_JOBS):

            job = job_dict.get(job_id)

            if job is None:

                # Henüz sisteme gelmemiş iş
                deadline_states.append(37)

            elif job.status in ["completed", "cancelled"]:

                # Tamamlanmış veya iptal edilmiş iş
                deadline_states.append(36)

            else:

                remaining_due = (
                    job.due_date - self.current_time
                )

                # Değerleri -35 ile +35 arasında sınırla
                remaining_due = max(
                    -35,
                    min(remaining_due, 35)
                )

                deadline_states.append(remaining_due)

        # 4. ACİL SİPARİŞ BİLGİSİ

        emergency_exists = int(

            any(job.is_emergency for job in self.jobs)

        )

        # 5. ZAMAN BİLGİSİ

        time_state = min(self.current_time, 35)

        # 6. TÜM BİLGİLERİ BİRLEŞTİR

        state = tuple(

            machine_states
            + [
                waiting_mask,
                completed_mask,
                urgent_mask
            ]
            + deadline_states
            + [
                emergency_exists,
                time_state
            ]

        )

        return state


    # ======================================
    # GEÇERLİ EYLEMLERİ BULMA
    # ======================================

    def get_valid_actions(self):

        valid_actions = []

        MAX_JOBS = 12

        for machine in self.machines:

            if machine.status != "idle":
                continue

            for job in self.jobs:

                if job.job_id >= MAX_JOBS:
                    continue

                if job.status != "waiting":
                    continue

                if machine.machine_id not in job.processing_times:
                    continue

                if job.mold_type not in machine.compatible_molds:
                    continue

                action = (

                    machine.machine_id * MAX_JOBS
                    + job.job_id

                )

                valid_actions.append(action)

        # Bekleme eylemi

        valid_actions.append(36)

        return valid_actions

    # ======================================
    # EYLEM NUMARASINI ÇÖZÜMLEME
    # ======================================

    def decode_action(self, action):

        MAX_JOBS = 12

        if action == 36:

            return None, None

        machine_id = action // MAX_JOBS

        job_id = action % MAX_JOBS

        return machine_id, job_id

    # ======================================
    # ÖDÜL HESAPLAMA
    # ======================================

    def calculate_reward(self):

        reward = 0

        for job in self.jobs:

            if job.status != "completed":

                continue

            if job.completion_time == self.current_time:

                reward += 20

                if job.completion_time <= job.due_date:

                    reward += 15

                if job.is_emergency:

                    reward += 25

        for job in self.jobs:

            if (

                job.status not in ["completed", "cancelled"]

                and self.current_time > job.due_date

            ):

                reward -= 2

        return reward

    # ======================================
    # Q-LEARNING STEP FONKSİYONU
    # ======================================

    def step(self, action):

        if self.done:

            return self.get_state(), 0, True, {}

        reward = 0

        completed_before = {

            job.job_id

            for job in self.jobs

            if job.status == "completed"

        }

        valid_actions = self.get_valid_actions()

        # Eylem kontrolü

        if action not in valid_actions:

            reward -= 15

        elif action == 36:

            reward -= 1

        else:

            machine_id, job_id = self.decode_action(action)

            success = self.assign_job(machine_id, job_id)

            if success:

                machine = self.machines[machine_id]

                if machine.status == "setup":

                    reward -= 5

            else:

                reward -= 15

        # Zamanı ilerlet

        self.step_time()

        # Acil sipariş
        if self.current_time == 5:

            self.add_emergency_job()

        # Rastgele arıza

        for machine in self.machines:

            if (

                machine.machine_id not in self.broken_once

                and machine.status in ["idle", "busy"]

                and 3 <= self.current_time <= 25

            ):

                if random.random() < 0.02:

                    if self.trigger_breakdown(machine.machine_id):

                        self.broken_once.add(machine.machine_id)

                        reward -= 8

       
        # ======================================
        # TAMAMLANAN İŞLER İÇİN ÖDÜL
        # ======================================

        for job in self.jobs:

            if (
                job.status == "completed"
                and job.job_id not in completed_before
            ):

                # İş tamamlandığı için temel ödül
                reward += 20

                # Zamanında tamamlanma ödülü
                if job.completion_time <= job.due_date:

                    reward += 20

                else:

                    # Geç tamamlanan iş için ek gecikme cezası
                    lateness = (
                        job.completion_time - job.due_date
                    )

                    reward -= min(lateness * 2, 30)

                # Acil sipariş tamamlama ödülü
                if job.is_emergency:

                    reward += 30

        # ======================================
        # DEVAM EDEN GECİKMELER İÇİN CEZA
        # ======================================

        for job in self.jobs:

            if (
                job.status not in ["completed", "cancelled"]
                and self.current_time > job.due_date
            ):

                reward -= 3


        # Simülasyon bitiş kontrolü

        if self.is_finished():

            self.done = True

        info = {

            "time": self.current_time,

            "completed_jobs": sum(

                job.status == "completed"

                for job in self.jobs

            ),

            "waiting_jobs": sum(

                job.status == "waiting"

                for job in self.jobs

            ),

            "machine_states": [

                machine.status

                for machine in self.machines

            ]

        }

        return (

            self.get_state(),

            reward,

            self.done,

            info

        )

    # ======================================
    # SİMÜLASYON BİTİŞ KONTROLÜ
    # ======================================

    def is_finished(self):

        all_completed = all(

            job.status == "completed"

            for job in self.jobs

        )

        all_machines_idle = all(

            machine.status == "idle"

            for machine in self.machines

        )

        return (

            all_completed

            and all_machines_idle

        ) or self.done

    # ======================================
    # FABRİKA DURUMUNU GÖSTERME
    # ======================================

    def show_status(self):

        print("\n========== FABRIKA DURUMU ==========")

        print("Zaman:", self.current_time)

        print("\nMAKINELER")

        for machine in self.machines:

            print(

                f"Makine {machine.machine_id + 1} | "

                f"Durum: {machine.status} | "

                f"Kalip: {machine.current_mold} | "

                f"Kalan sure: {machine.remaining_time}"

            )

        print("\nISLER")

        for job in self.jobs:

            print(

                f"Is {job.job_id} | "

                f"Durum: {job.status} | "

                f"Teslim: {job.due_date} | "

                f"Oncelik: {job.priority}"

            )

        print("====================================")


# ==========================================
# 4. TEST
# ==========================================

if __name__ == "__main__":

    env = JobShopEnv()

    print("\n========== MDP TESTI ==========")

    # Başlangıç durumu

    state = env.get_state()

    print("\nState:")

    print(state)

    print("\nState uzunluğu:")

    print(len(state))

    # Geçerli eylemler

    actions = env.get_valid_actions()

    print("\nGeçerli eylemler:")

    print(actions)

    # İlk eylemi seç

    action = actions[0]

    print("\nSeçilen eylem:", action)

    # Ortamda bir adım ilerle

    next_state, reward, done, info = env.step(action)

    print("\nYeni State:")

    print(next_state)

    print("\nReward:")

    print(reward)

    print("\nDone:")

    print(done)

    print("\nInfo:")

    print(info)

    env.show_status()

    print("\n========== TEST TAMAMLANDI ==========")
