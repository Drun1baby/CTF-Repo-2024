import logging
import multiprocessing

from nicegui import app
from rich.logging import RichHandler

from . import pages as pages

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[RichHandler(rich_tracebacks=True)],
)


if (
    not app.config.has_run_config
    and multiprocessing.current_process().name != "MainProcess"
):
    from .__main__ import main

    logger = logging.getLogger(__name__)
    logger.warning("Running in a subprocess, starting main()")

    main()


__all__ = ["app"]
