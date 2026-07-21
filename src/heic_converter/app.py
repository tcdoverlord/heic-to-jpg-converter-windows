from __future__ import annotations

import logging
import sys
from pathlib import Path

from .cli import run_cli
from .gui import launch_gui
from .logging_setup import configure_logging


def main(arguments: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if arguments is None else arguments)
    log_path = configure_logging()
    logging.getLogger(__name__).info("Application started with arguments: %s", args)

    if "--cli" in args:
        cli_args = [argument for argument in args if argument != "--cli"]
        return run_cli(cli_args)

    initial_sources = [
        Path(argument)
        for argument in args
        if not argument.startswith("-") and Path(argument).exists()
    ]
    logging.getLogger(__name__).info("Session log: %s", log_path)
    return launch_gui(initial_sources=initial_sources)
