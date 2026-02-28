from __future__ import annotations

import os

from ..ai.agent import AgentConfig, DQNAgent
from ..env.rollout import run_episode
from ..env.trex_env import TrexEnv
from ..paths import RunPaths


def play(args, run: RunPaths, assets) -> None:
    env = TrexEnv(args, assets, render=bool(args.render))

    agent = None
    if not bool(args.human):
        cfg = AgentConfig(
            obs_dim=9,
            n_actions=3,
            gamma=args.gamma,
            lr=args.lr,
            batch_size=args.batch_size,
            buffer_size=args.buffer_size,
            train_start=args.train_start,
            target_update=args.target_update,
            epsilon_start=0.0,
            epsilon_end=0.0,
            epsilon_decay_steps=1,
        )
        agent = DQNAgent(cfg)

        model_dir = args.model
        if not model_dir:
            # fallback: best du run courant
            model_dir = run.best_dir
        if os.path.isdir(model_dir):
            agent.load(model_dir)
        else:
            raise FileNotFoundError(f"Model dir not found: {model_dir}")

    res = run_episode(env, agent=agent, training=False, human=bool(args.human), max_steps=args.max_steps)
    print(f"Score: {int(res.score)}  Steps: {res.steps}  Reward: {res.total_reward:.1f}")
    env.close()
