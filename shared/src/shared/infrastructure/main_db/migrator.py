import logging
import subprocess

logger = logging.getLogger(__name__)

async def apply_migrations(url: str) -> None:
    migrations_is_ok = subprocess.call(["alembic", "-x", f"db_url={url}", "upgrade", "head"]) == 0
    if not migrations_is_ok:
        logger.error("There is an error while upgrading database")
        exit(1)
