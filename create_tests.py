#!/usr/bin/env python3
import asyncio
import datetime

import httpx

# === CONFIGURATION ===
URL = "https://ai.avocado.ceo/api/post-to-publish"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhYzIzNzE5OS0xYjlmLTQ0YjEtYWIyYy04NzFlOWEwNDBlZmEiLCJleHAiOjE3NTE3NjgyMTUsImlzcyI6ImFzc2lzdGFudC1hZG1pbi1iYWNrIiwiYXVkIjoiYXNzaXN0YW50LWFkbWluLWZyb250In0.9XycyVPKJlTFvd1wgeBj9ui0-4I5y_zNN4Bttq0uS64"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}",
}

BODY_TEMPLATE = {
    "post_id": "3cef2321-1d90-4670-b102-8612a9bc8c37",
    "scheduled_type": "everyday",
    "responsible_manager_id": "70c81f07-ab4a-4794-b33e-2aab81eef36e",
    "scheduled_date": None,
    # "scheduled_time" filled in per-task
    "chat_ids": [
        "be6ffc15-665e-4c8d-8353-692b1754259c",
        "e28ee4f5-985c-4b59-9b64-43ec917761ad",
        "e7241e0d-dca5-4958-839d-b0e8c658a7cc",
        "d3dee63d-1337-4875-beb9-904fb844061c",
        "37640e1d-9d67-4ddd-9157-4b486141b28a"
    ],
    "manager_id": "ac237199-1b9f-44b1-ab2c-871e9a040efa",
    "status": "pending"
}

async def send_at(client: httpx.AsyncClient, time_str: str):
    """Fire one POST with scheduled_time = time_str."""
    payload = BODY_TEMPLATE.copy()
    payload["scheduled_time"] = time_str
    resp = await client.post(URL, json=payload, headers=HEADERS)
    if resp.status_code == 200:
        print(f"✓ Scheduled at {time_str}")
    else:
        print(f"✗ Failed at {time_str}: {resp.status_code} — {resp.text!r}")

async def main():
    # build all the 15-minute timestamps from 00:00 to 23:45
    t = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
    end = t + datetime.timedelta(days=1)

    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = []
        while t < end:
            ts = t.time().strftime("%H:%M")
            tasks.append(send_at(client, ts))
            t += datetime.timedelta(minutes=15)

        # run them concurrently
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
