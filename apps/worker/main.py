"""Asynchronous background worker entry point for Morrow."""

import asyncio
import signal
from typing import Any

from core.config.settings import get_settings
from core.logging.logger import get_logger, setup_logging

logger = get_logger(__name__)


class Worker:
    """Async background worker daemon."""

    def __init__(self) -> None:
        self._running = False

    async def start(self) -> None:
        """Start the background processing loop."""
        self._running = True
        logger.info("Morrow background worker started.")
        while self._running:
            # Future phases: process scheduled ingestion, consolidation, and background jobs
            await asyncio.sleep(1)

    def stop(self, *args: Any) -> None:
        """Signal worker to terminate gracefully."""
        logger.info("Worker received shutdown signal.")
        self._running = False


async def run_worker() -> None:
    """Initialize environment and execute the worker lifecycle."""
    settings = get_settings()
    setup_logging(level=settings.log_level, log_format=settings.log_format)
    logger.info("Initializing worker for %s (env=%s)", settings.app_name, settings.app_env)

    worker = Worker()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, worker.stop)
        except NotImplementedError:
            # Signal handlers may not be supported on non-UNIX event loops
            pass

    await worker.start()


if __name__ == "__main__":
    asyncio.run(run_worker())
