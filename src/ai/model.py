from __future__ import annotations

import tensorflow as tf


def build_q_network(input_dim: int, n_actions: int, lr: float) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(input_dim,), dtype=tf.float32)
    x = tf.keras.layers.Dense(64, activation="relu")(inputs)
    x = tf.keras.layers.Dense(64, activation="relu")(x)
    outputs = tf.keras.layers.Dense(n_actions, activation=None)(x)
    model = tf.keras.Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=lr), loss="mse")
    return model
