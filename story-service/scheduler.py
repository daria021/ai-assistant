from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from services.story import publish_story

scheduler = AsyncIOScheduler()

def schedule_story(story_id: int, run_date):
    scheduler.add_job(
        func=publish_story,
        trigger=DateTrigger(run_date=run_date),
        args=[story_id],
        id=f"story_{story_id}",
        replace_existing=True,
    )
