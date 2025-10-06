import pathlib
from uuid import uuid4

import imageio
from typing import Optional
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
    logger.info(f"Начало конвертации .tgs файла, размер: {len(tgs_bytes)} байт")

    # Проверяем начало файла для определения формата
    if len(tgs_bytes) >= 4:
        magic_bytes = tgs_bytes[:4]
        logger.info(f"Первые 4 байта файла: {magic_bytes.hex()}")

        # Проверяем различные форматы
        if magic_bytes == b'\x1f\x8b\x08\x00':  # gzip magic bytes
            logger.info("Файл выглядит как gzip-сжатый (.tgs обычно gzip)")
        elif magic_bytes.startswith(b'RIFF'):  # WebP magic bytes
            logger.info("Файл уже в формате WebP!")
        elif magic_bytes.startswith(b'WEBP'):  # WebP magic bytes variant
            logger.info("Файл уже в формате WebP!")
        elif magic_bytes == b'PK\x03\x04':  # ZIP magic bytes
            logger.info("Файл выглядит как ZIP (возможно новый формат .tgs)")
        else:
            logger.warning(f"Неизвестный формат файла, magic bytes: {magic_bytes.hex()}")

    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / f"{uuid4()}.tgs"
        dst = pathlib.Path(td) / f"{uuid4()}.webp"
        src.write_bytes(tgs_bytes)

        # Попробуем разные форматы вывода
        conversion_attempts = [
            # Сначала попробуем конвертировать в GIF, потом в WebP через imageio
            ([_LOTTIE, str(src), str(dst).replace('.webp', '.gif')], "gif_to_webp"),
            # Прямой WebP (если сработает)
            ([_LOTTIE, str(src), str(dst)], "direct_webp"),
        ]

        for attempt_num, (cmd, method) in enumerate(conversion_attempts, 1):
            logger.info(f"Попытка конвертации #{attempt_num} методом {method}: {' '.join(cmd)}")

            try:
                if method == "gif_to_webp":
                    # Конвертируем в GIF с помощью lottie
                    gif_path = cmd[-1]  # последний аргумент - путь к GIF
                    proc = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    out, err = await proc.communicate()

                    if proc.returncode == 0 and pathlib.Path(gif_path).exists():
                        logger.info("GIF создан успешно, конвертируем в WebP")
                        # Конвертируем GIF в WebP с помощью imageio
                        try:
                            import imageio
                            reader = imageio.get_reader(gif_path)
                            writer = imageio.get_writer(str(dst), format='webp', mode='I')
                            for frame in reader:
                                writer.append_data(frame)
                            writer.close()
                            reader.close()

                            if dst.exists():
                                logger.info("Конвертация GIF→WebP успешна!")
                                return dst.read_bytes()
                        except Exception as gif_err:
                            logger.warning(f"Ошибка конвертации GIF→WebP: {gif_err}")
                    else:
                        stderr_text = err.decode().strip() if err else ""
                        logger.warning(f"Не удалось создать GIF: {stderr_text}")

                elif method == "direct_webp":
                    # Прямой WebP
                    proc = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    out, err = await proc.communicate()

                    stdout_text = out.decode().strip() if out else ""
                    stderr_text = err.decode().strip() if err else ""

                    logger.info(f"Код возврата: {proc.returncode}")
                    if stdout_text:
                        logger.info(f"STDOUT: {stdout_text}")
                    if stderr_text:
                        logger.info(f"STDERR: {stderr_text}")

                    if proc.returncode == 0 and dst.exists():
                        logger.info("Прямая конвертация WebP успешна!")
                        return dst.read_bytes()

                logger.warning(f"Попытка #{attempt_num} ({method}) не удалась")

            except Exception as e:
                logger.warning(f"Ошибка при попытке #{attempt_num} ({method}): {e}")
                continue

        # Если все попытки провалились
        logger.error("Все конвертеры провалились")
        logger.error("Последняя ошибка:\n%s", (err or out).decode().strip() if 'err' in locals() else "Нет информации об ошибке")
        raise RuntimeError("Ошибка конвертации .tgs → .webp (см. лог)")


def _sync_convert_tgs_to_webm_bytes(tgs_bytes: bytes) -> Optional[bytes]:
    """Конвертация .tgs → .webm через PyRlottie (tgs→webp) + imageio(ffmpeg) webp→webm.
    Возвращает байты .webm или None при неудаче.
    """
    try:
        from pyrlottie import convLottie
    except Exception as e:
        logger.warning("PyRlottie недоступен: %s", e)
        return None

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        src = tmp / f"{uuid4()}.tgs"
        src.write_bytes(tgs_bytes)

        # 1) tgs → animated webp
        webp_path = tmp / f"{uuid4()}.webp"
        try:
            logger.info("rlottie: start → %s", webp_path)
            # Используем синхронный API pyrlottie
            convLottie(str(src), str(webp_path))
        except Exception as e:
            logger.exception("PyRlottie webp export failed: %s", e)
            return None
        if not webp_path.exists():
            logger.warning("rlottie: webp not created")
            return None

        # 2) animated webp → webm
        output_webm = tmp / f"{uuid4()}.webm"
        try:
            logger.info("ffmpeg(imageio): webp→webm → %s", output_webm)
            reader = imageio.get_reader(str(webp_path))
            meta = reader.get_meta_data()
            fps = meta.get('fps', 24)
            writer = imageio.get_writer(str(output_webm), format='FFMPEG', mode='I', fps=fps, codec='libvpx-vp9')
            for frame in reader:
                writer.append_data(frame)
            writer.close()
            reader.close()
        except Exception as e:
            logger.exception("webp→webm failed: %s", e)
            return None

        if not output_webm.exists():
            logger.warning("ffmpeg: webm not created")
            return None
        data = output_webm.read_bytes()
        logger.info("tgs→webm: done, size=%d", len(data))
        return data


async def convert_tgs_to_webm(tgs_bytes: bytes) -> bytes:
    """Async-обёртка вокруг _sync_convert_tgs_to_webm_bytes."""
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, _sync_convert_tgs_to_webm_bytes, tgs_bytes)
    if not data:
        raise RuntimeError("Не удалось конвертировать .tgs → .webm")
    return data
