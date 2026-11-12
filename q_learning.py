
import numpy as np
import random
import pickle
import os


# ==========================================
# Q-LEARNING AJANI
# ==========================================

class QLearningAgent:

    def __init__(

        self,

        action_size=37,

        learning_rate=0.1,

        discount_factor=0.95,

        epsilon=1.0,

        epsilon_min=0.01,

        epsilon_decay=0.995

    ):

        # Eylem sayısı
        self.action_size = action_size

        # Öğrenme parametreleri
        self.alpha = learning_rate
        self.gamma = discount_factor

        # Keşif parametreleri
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # Q-Tablosu
        # Her karşılaşılan durum için 37 eylem değeri tutulur.
        self.q_table = {}

    # ======================================
    # DURUMU Q-TABLOSUNA EKLEME
    # ======================================

    def get_q_values(self, state):

        if state not in self.q_table:

            self.q_table[state] = np.zeros(
                self.action_size,
                dtype=np.float64
            )

        return self.q_table[state]

    # ======================================
    # EYLEM SEÇME (EPSILON-GREEDY)
    # ======================================

    def choose_action(self, state, valid_actions):

        if not valid_actions:

            return 36

        # Keşif: Rastgele geçerli eylem seç
        if random.random() < self.epsilon:

            return random.choice(valid_actions)

        # Sömürü: En yüksek Q değerine sahip eylemi seç
        q_values = self.get_q_values(state)

        valid_q_values = {

            action: q_values[action]

            for action in valid_actions

        }

        max_value = max(valid_q_values.values())

        # Eşit Q değerlerinde rastgele seçim
        best_actions = [

            action

            for action, value in valid_q_values.items()

            if value == max_value

        ]

        return random.choice(best_actions)

    # ======================================
    # Q-TABLOSU GÜNCELLEME
    # ======================================

    def update(

        self,

        state,

        action,

        reward,

        next_state,

        done,

        next_valid_actions

    ):

        current_q_values = self.get_q_values(state)

        current_q = current_q_values[action]

        # Terminal durum
        if done or not next_valid_actions:

            max_next_q = 0

        else:

            next_q_values = self.get_q_values(next_state)

            max_next_q = max(

                next_q_values[a]

                for a in next_valid_actions

            )

        # Bellman güncellemesi
        new_q = current_q + self.alpha * (

            reward
            + self.gamma * max_next_q
            - current_q

        )

        current_q_values[action] = new_q

    # ======================================
    # EPSILON AZALTMA
    # ======================================

    def decay_epsilon(self):

        self.epsilon = max(

            self.epsilon_min,

            self.epsilon * self.epsilon_decay

        )

    # ======================================
    # Q-TABLOSUNU KAYDETME
    # ======================================

    def save(self, path="results/q_table.pkl"):

        os.makedirs("results", exist_ok=True)

        data = {

            "q_table": self.q_table,

            "epsilon": self.epsilon,

            "alpha": self.alpha,

            "gamma": self.gamma

        }

        with open(path, "wb") as file:

            pickle.dump(data, file)

        print("Q-Tablosu kaydedildi:", path)

    # ======================================
    # Q-TABLOSUNU YÜKLEME
    # ======================================

    def load(self, path="results/q_table.pkl"):

        with open(path, "rb") as file:

            data = pickle.load(file)

        self.q_table = data["q_table"]

        self.epsilon = data["epsilon"]

        self.alpha = data["alpha"]

        self.gamma = data["gamma"]

        print("Q-Tablosu yuklendi:", path)

    # ======================================
    # Q-TABLOSU BİLGİLERİ
    # ======================================

    def show_info(self):

        print("\n========== Q-LEARNING BILGILERI ==========")

        print("Durum sayisi:", len(self.q_table))

        print("Eylem sayisi:", self.action_size)

        print("Learning Rate:", self.alpha)

        print("Discount Factor:", self.gamma)

        print("Epsilon:", self.epsilon)

        print("==========================================")


# ==========================================
# Q-LEARNING TEST
# ==========================================

if __name__ == "__main__":

    agent = QLearningAgent()

    # Örnek durum
    state = (0, 0, 0, 0, 0)

    # Geçerli eylemler
    valid_actions = [0, 1, 5, 10, 36]

    # Eylem seç
    action = agent.choose_action(
        state,
        valid_actions
    )

    print("Secilen eylem:", action)

    # Yeni durum
    next_state = (1, 0, 0, 0, 1)

    # Ödül
    reward = 20

    # Q değerini güncelle
    agent.update(

        state,

        action,

        reward,

        next_state,

        False,

        valid_actions

    )

    print("\nGuncellenmis Q degeri:")

    print(agent.q_table[state][action])

    # Ajan bilgileri
    agent.show_info()
