from __future__ import annotations

import os
from collections import deque
from typing import Deque

import numpy as np

from ..ai.agent import AgentConfig, DQNAgent
from ..env.trex_env import TrexEnv
from ..paths import RunPaths, save_args
from .logger import CSVLogger


def train(args, run: RunPaths, assets) -> None:
    save_args(run.logs_run_dir, args)
    logger = CSVLogger(run.logs_run_dir)

    env = TrexEnv(args, assets, render=bool(args.render))

    cfg = AgentConfig(
        obs_dim=9,
        n_actions=3,
        gamma=args.gamma,
        lr=args.lr,
        batch_size=args.batch_size,
        buffer_size=args.buffer_size,
        train_start=args.train_start,
        target_update=args.target_update,
        epsilon_start=args.epsilon_start,
        epsilon_end=args.epsilon_end,
        epsilon_decay_steps=args.epsilon_decay_steps,
    )
    agent = DQNAgent(cfg)

    if args.resume:
        agent.load(args.resume)

    recent_scores: Deque[float] = deque(maxlen=20)
    best_avg = agent.best_score or 0.0
    train_freq = args.train_freq  # Train every N steps

    for ep in range(1, args.episodes + 1):
        obs = env.reset()
        total_reward = 0.0
        steps = 0
        losses = []

        while True:
            dt = env.tick()
            action = agent.act(obs, training=True)
            step_res = env.step(action, dt)
            next_obs, reward, done = step_res.obs, step_res.reward, step_res.done

            agent.remember(obs, action, reward, next_obs, done)

            # Train only every train_freq steps (faster!)
            if steps % train_freq == 0:
                loss = agent.train_step()
                if loss is not None:
                    losses.append(loss)

            obs = next_obs
            total_reward += reward
            steps += 1

            if env.render_enabled:
                if env.render():
                    break

            if done or steps >= args.max_steps:
                break

        score = step_res.info["score"]
        loss_avg = float(np.mean(losses)) if losses else None
        recent_scores.append(score)
        avg20 = float(np.mean(recent_scores))

        if (ep % args.save_every) == 0:
            agent.save(run.latest_dir)

        if avg20 > best_avg:
            best_avg = avg20
            agent.best_score = best_avg
            agent.save(run.best_dir)

        logger.log(ep, score, total_reward, steps, agent.epsilon, loss_avg)

        if args.render:
            print(f"[EP {ep}] score={int(score)} reward={total_reward:.1f} eps={agent.epsilon:.3f}")
        else:
            if ep % 10 == 0:
                print(f"[EP {ep}] score={int(score)} avg20={avg20:.1f} eps={agent.epsilon:.3f}")

    agent.save(run.latest_dir)
    env.close()
