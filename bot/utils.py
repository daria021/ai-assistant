import asyncio
import os

import imageio


def _sync_convert_webm_to_webp(input_path: str) -> str:
    """
    Synchronous helper that reads a .webm and writes an animated .webp
    with the same basename.
    """
    # derive output path
    base, _ = os.path.splitext(input_path)
    output_path = f"{base}.webp"

    reader = imageio.get_reader(input_path, 'ffmpeg')
    meta = reader.get_meta_data()
    fps = meta.get('fps', 24)  # fallback to 24fps if absent

    writer = imageio.get_writer(
        output_path,
        format='webp',
        mode='I',
        duration=1 / fps
    )

    for frame in reader:
        writer.append_data(frame)

    writer.close()
    reader.close()

    return output_path


async def convert_webm_to_webp(input_path: str) -> str:
    """
    Async wrapper that offloads the blocking conversion to a thread executor.
    Returns the path to the created .webp file.
    """
    loop = asyncio.get_running_loop()
    output_path = await loop.run_in_executor(
        None,  # uses default ThreadPoolExecutor
        _sync_convert_webm_to_webp,
        input_path
    )
    return output_path
