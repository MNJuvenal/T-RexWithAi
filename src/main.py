from __future__ import annotations

import os


def _init_pygame_for_assets(render: bool) -> None:
    # convert_alpha() needs a video mode set.
    if not render:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame

    pygame.init()
    # Minimal display so convert_alpha works
    pygame.display.set_mode((1, 1))


def main() -> None:
    from .cli import build_parser
    from .paths import prepare_run_dirs
    from .game.assets import load_assets
    from .utils import set_seed
    from .training.train import train
    from .training.eval import play

    args = build_parser().parse_args()

    set_seed(args.seed)
    _init_pygame_for_assets(render=bool(args.render))

    assets = load_assets(os.path.join(os.path.dirname(__file__), "..", "assets"))

    run = prepare_run_dirs(args.models_dir, args.logs_dir, args.run_name, resume=args.resume)

    if args.train:
        train(args, run, assets)
    else:
        play(args, run, assets)


if __name__ == "__main__":
    main()
