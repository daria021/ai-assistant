import asyncio
import logging
from datetime import datetime, timedelta
from uuid import UUID

from shared.infrastructure.main_db import init_db
from shared.domain.enums import PublicationStatus, ScheduledType
from shared.dependencies.services.get_scheduler import get_scheduler
from apscheduler.events import EVENT_JOB_MISSED

from dependencies.services.consumer import get_posts_consumer
from shared.dependencies.repositories.post_to_publish import get_post_to_publish_repository
from dependencies.services.posting import get_posting_service
from settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

async def main():
    logger.info("Starting posting service")

    init_db(settings.db.url)

    # bootstrap: re-schedule posts into APScheduler on clean scheduler DB,
    # with filters to avoid re-scheduling terminal or stale singles
    try:
        repo = get_post_to_publish_repository()
        scheduler = get_scheduler(settings.scheduler.job_store_sqlite_path)

        async def _handle_missed_job(job_id: str):
            try:
                if job_id.startswith("post_") and not job_id.startswith("post_daily_"):
                    post_id_str = job_id.split("post_", 1)[1]
                    post_uuid = UUID(post_id_str)
                    logger.info(f"Marking missed one-off publication {post_uuid} as STALE due to job misfire")
                    await repo.set_status(post_uuid, PublicationStatus.STALE)
            except Exception as e:
                logger.error(f"Failed to handle missed job {job_id}: {e}", exc_info=True)

        def _on_scheduler_event(event):
            try:
                if getattr(event, 'code', None) == EVENT_JOB_MISSED:
                    job_id = getattr(event, 'job_id', None)
                    if job_id:
                        asyncio.create_task(_handle_missed_job(job_id))
            except Exception:
                logger.error("Error in scheduler listener", exc_info=True)

        scheduler.add_listener(_on_scheduler_event, mask=EVENT_JOB_MISSED)
        posting_service = get_posting_service()
        posts = await repo.get_all(limit=10000, offset=0)
        logger.info(f"Bootstrap scheduling: restoring {len(posts)} posts into scheduler")
        grace = timedelta(minutes=settings.bootstrap.single_miss_grace_minutes)
        now = datetime.now()

        terminal_statuses = {
            PublicationStatus.POSTED,
            PublicationStatus.FAILED,
            PublicationStatus.CANCELED,
            PublicationStatus.STALE,
        }

        restored = 0
        skipped_terminal = 0
        marked_stale = 0

        for p in posts:
            try:
                # Skip terminal statuses entirely
                if p.status in terminal_statuses:
                    skipped_terminal += 1
                    continue

                # Handle SINGLE posts that are long past due
                if p.scheduled_type == ScheduledType.SINGLE and p.scheduled_date is not None:
                    scheduled_at = datetime.combine(p.scheduled_date, p.scheduled_time)
                    if scheduled_at + grace < now:
                        # Mark publication as STALE (won't be executed automatically)
                        await repo.set_status(p.id, PublicationStatus.STALE)
                        marked_stale += 1
                        continue

                await posting_service.schedule_post(p)
                restored += 1
            except Exception as e:
                logger.error(f"Failed to restore scheduling for post {getattr(p, 'id', '?')}: {e}")
        logger.info(
            "Bootstrap summary: restored=%s, skipped_terminal=%s, marked_stale=%s",
            restored, skipped_terminal, marked_stale,
        )
    except Exception:
        logger.error("Bootstrap scheduling failed", exc_info=True)

    consumer = get_posts_consumer()

    try:
        await consumer.execute()
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, shutting down...")
        exit(0)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        exit(1)


logger.info(__name__)

if __name__ == "__main__":

    asyncio.run(main())
