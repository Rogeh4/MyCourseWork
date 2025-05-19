import numpy as np
import pickle
from collections import defaultdict


class QLearningAgent:
    def __init__(self):
        self.ALPHA = 0.3  # Увеличенная скорость обучения
        self.GAMMA = 0.95  # Сниженный дисконт-фактор
        self.EPSILON_START = 0.5  # Больше исследований
        self.EPSILON_DECAY = 0.999  # Медленнее снижение
        self.EPSILON_MIN = 0.05

        self.Q = defaultdict(lambda: np.zeros(3))
        self.epsilon = self.EPSILON_START
        self.episode = 0

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.choice([0, 1, 2])  # 0: stay, 1: up, 2: down
        q_values = self.Q[state]
        return np.argmax(q_values)

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.Q[next_state])
        td_target = reward + self.GAMMA * self.Q[next_state][best_next_action]
        td_error = td_target - self.Q[state][action]
        self.Q[state][action] += self.ALPHA * td_error

    def decay_epsilon(self):
        if self.epsilon > self.EPSILON_MIN:
            self.epsilon *= self.EPSILON_DECAY

    def save_model(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(dict(self.Q), f)

    def load_model(self, filename):
        try:
            with open(filename, 'rb') as f:
                self.Q = defaultdict(lambda: np.zeros(3), pickle.load(f))
        except FileNotFoundError:
            print("Model not found. Starting from scratch.")