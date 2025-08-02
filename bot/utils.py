import pathlib
from uuid import uuid4

import imageio
import asyncio, tempfile, os, logging
import shutil

logger = logging.getLogger(__name__)

LOTTIE_BIN = (
    shutil.which("lottie_convert")                # ищем без .py
    or shutil.which("lottie_convert.py")          # или с .py
    or "/usr/local/bin/lottie_convert.py"         # жёсткий fallback
)
if not os.path.isfile(LOTTIE_BIN):
    raise RuntimeError(f"LOTTIE_BIN not found at {LOTTIE_BIN}")

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

# определяем бинарь-конвертер один раз
_LOTTIE = (
    shutil.which("lottie_convert") or
    shutil.which("lottie_convert.py") or
    "/usr/local/bin/lottie_convert.py"
)
if not os.path.isfile(_LOTTIE):
    raise RuntimeError("lottie_convert не найден — установите lottie[cli]")

async def convert_tgs_to_webp(tgs_bytes: bytes) -> bytes:
    """
    Конвертирует .tgs (Lottie) прямо в анимированный .webp.
    Возвращает готовый байт-массив WEBP.
    """
    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / f"{uuid4()}.tgs"
        dst = pathlib.Path(td) / f"{uuid4()}.webp"
        src.write_bytes(tgs_bytes)

        proc = await asyncio.create_subprocess_exec(
            _LOTTIE, str(src), str(dst),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc.communicate()

        if proc.returncode != 0 or not dst.exists():
            logger.error("lottie_convert error:\n%s", (err or out).decode().strip())
            raise RuntimeError("Ошибка конвертации .tgs → .webp (см. лог)")

        return dst.read_bytes()
