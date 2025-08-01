import imageio
import asyncio, tempfile, os, logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _sync_convert_webm_to_webp(input_path: str) -> str:
    """
    Synchronous helper that reads a .webm and writes an animated .webp
    with the same basename.
    """
    # derive output path
    logger.info(f"Converting webm to webp {input_path}")
    base, ext = os.path.splitext(input_path)
    logger.info(f"Converting webp to webp {base}, {ext}")
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


async def convert_tgs_to_webm(tgs_bytes: bytes) -> str:
    """
    Принимает raw-байты .tgs, возвращает путь к временно
    созданному .webm-файлу (анимированному).
    Вызывать внутри `with tempfile.TemporaryDirectory()`.
    """
    with tempfile.TemporaryDirectory() as td:
        in_path  = Path(td) / "in.tgs"
        out_path = Path(td) / "out.webm"
        in_path.write_bytes(tgs_bytes)

        # lottie_convert.py in.tgs out.webm --format webm
        proc = await asyncio.create_subprocess_exec(
            "lottie_convert.py", str(in_path), str(out_path), "--format", "webm"
        )
        await proc.communicate()

        if not out_path.exists():
            raise RuntimeError("lottie_convert: out.webm not produced")

        # возвращаем КОПИЮ, чтобы файл не удалился вместе с tmpdir
        final_path = Path(td).with_suffix(".webm")
        final_path.write_bytes(out_path.read_bytes())
        logger.info("tgs -> webm: %s → %s", in_path, final_path)
        return str(final_path)
