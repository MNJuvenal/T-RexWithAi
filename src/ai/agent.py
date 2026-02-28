from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Optional

import numpy as np
import tensorflow as tf

from .buffer import ReplayBuffer
from .checkpoint import TrainState, load_state, save_state
from .model import build_q_network


@dataclass
class AgentConfig:
    obs_dim: int
    n_actions: int
    gamma: float
    lr: float
    batch_size: int
    buffer_size: int
    train_start: int
    target_update: int
    epsilon_start: float
    epsilon_end: float
    epsilon_decay_steps: int


class DQNAgent:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg
        self.q = build_q_network(cfg.obs_dim, cfg.n_actions, cfg.lr)
        self.target = build_q_network(cfg.obs_dim, cfg.n_actions, cfg.lr)
        self.target.set_weights(self.q.get_weights())

        self.buffer = ReplayBuffer(cfg.buffer_size)
        self.step_count = 0
        self.epsilon = cfg.epsilon_start
        self.best_score = 0.0

    def act(self, obs: np.ndarray, training: bool) -> int:
        if training and random.random() < self.epsilon:
            return random.randint(0, self.cfg.n_actions - 1)
        qvals = self.q(np.expand_dims(obs, axis=0), training=False).numpy()[0]
        return int(np.argmax(qvals))

    def remember(self, s, a, r, s2, d) -> None:
        self.buffer.add(s, a, r, s2, d)

    def _decay_epsilon(self) -> None:
        if self.cfg.epsilon_decay_steps <= 0:
            return
        frac = min(1.0, self.step_count / float(self.cfg.epsilon_decay_steps))
        self.epsilon = self.cfg.epsilon_start + frac * (self.cfg.epsilon_end - self.cfg.epsilon_start)
        self.epsilon = float(max(min(self.epsilon, self.cfg.epsilon_start), self.cfg.epsilon_end))

    def train_step(self) -> Optional[float]:
        self.step_count += 1
        self._decay_epsilon()

        if len(self.buffer) < self.cfg.train_start:
            return None

        batch = self.buffer.sample(self.cfg.batch_size)
        s = batch.s
        a = batch.a
        r = batch.r
        s2 = batch.s2
        d = batch.d

        # target Q
        q_next = self.target(s2, training=False).numpy()
        max_next = np.max(q_next, axis=1)
        y = r + (1.0 - d) * self.cfg.gamma * max_next

        q_pred = self.q(s, training=False).numpy()
        q_pred[np.arange(len(a)), a] = y

        loss = float(self.q.train_on_batch(s, q_pred))

        if self.step_count % self.cfg.target_update == 0:
            self.target.set_weights(self.q.get_weights())

        return loss

    def save(self, out_dir: str) -> None:
        os.makedirs(out_dir, exist_ok=True)
        self.q.save(os.path.join(out_dir, "model.keras"), overwrite=True)
        save_state(out_dir, TrainState(step=self.step_count, epsilon=self.epsilon, best_score=self.best_score))

    def load(self, in_dir: str) -> None:
        model_path = os.path.join(in_dir, "model.keras")
        if os.path.exists(model_path):
            self.q = tf.keras.models.load_model(model_path)
            # rebuild target with same arch
            self.target = tf.keras.models.clone_model(self.q)
            self.target.set_weights(self.q.get_weights())
            # compile target not necessary
        st = load_state(in_dir)
        if st:
            self.step_count = st.step
            self.epsilon = st.epsilon
            self.best_score = st.best_score
