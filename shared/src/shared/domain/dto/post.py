from typing import Optional, List

from pydantic import field_validator
from pydantic_core.core_schema import FieldValidationInfo

from .abstract import CreateDTO, UpdateDTO
from .post_to_publish import MessageEntityDTO

RHINO = '🦏'

class CreatePostDTO(CreateDTO):
    name: str
    text: str
    image_path: Optional[str] = None
    is_template: bool
    html: Optional[str] = None
    entities: Optional[list[MessageEntityDTO]] = None

    @field_validator("entities", mode="after")
    def check_bounds(cls, entities: List[MessageEntityDTO], info: FieldValidationInfo) -> List[MessageEntityDTO]:
        txt = info.data.get("text", "")
        custom_emojis, newlines = 0, txt.count('\n') * 2
        for e in entities:
            if e.type == 'custom_emoji':
                custom_emojis += 1

            text_len = len(txt) + custom_emojis + newlines
            if not (0 <= e.offset < text_len and e.offset + e.length <= text_len):
                raise ValueError(
                    f"Entity out of bounds: offset={e.offset} length={e.length} for text of length {text_len}")

        return entities


def _ui_total_len(s: str) -> int:
    """Длина текста в UI-единицах: CRLF и кастом-эмодзи считаются по 2."""
    # '\n' на фронте становится '\r\n' в multipart => +1 к каждой \n
    return len(s) + s.count('\n') + s.count(RHINO)


def _ui_step(ch: str) -> int:
    """Сколько UI-единиц занимает символ."""
    if ch == '\n':
        return 2  # CRLF
    if ch == RHINO:
        return 2  # кастом-эмодзи как 2 UTF-16 единицы
    return 1


def _ui_to_py_index(s: str, ui_index: int) -> int:
    """
    Маппинг: индекс в UI-единицах -> индекс для среза Python.
    Возвращает такой py-индекс, что s[py:...] попадает туда, где находится ui_index.
    """
    ui = 0
    py = 0
    for ch in s:
        step = _ui_step(ch)
        if ui + step > ui_index:
            # ui_index попадает внутрь текущего символа -> срез начинается здесь
            return py
        ui += step
        py += 1
    # если ui_index == точной UI-длине — вернуть конец строки
    return py


def _normalize_entities_from_ui_to_py(s: str, entities: List["MessageEntityDTO"]) -> List["MessageEntityDTO"]:
    """
    Пересчитывает offset/length из UI-метрики фронта в питоновские индексы.
    """
    normalized = []
    for e in entities:
        start_py = _ui_to_py_index(s, e.offset)
        end_py = _ui_to_py_index(s, e.offset + e.length)
        new_e = e.model_copy(deep=True)
        new_e.offset = start_py
        new_e.length = max(0, end_py - start_py)
        normalized.append(new_e)
    return normalized


class UpdatePostDTO(UpdateDTO):
    name: Optional[str] = None
    text: Optional[str] = None
    image_path: Optional[str] = None
    is_template: Optional[bool] = None
    html: Optional[str] = None
    entities: Optional[list["MessageEntityDTO"]] = None

    @field_validator("entities", mode="after")
    def check_bounds(cls, entities: List["MessageEntityDTO"], info: FieldValidationInfo) -> List["MessageEntityDTO"]:
        txt: str = info.data.get("text", "") or ""
        if not txt or not entities:
            return entities

        # 1) сначала валидируем по UI-метрике, как делает фронт
        ui_len = _ui_total_len(txt)
        for e in entities:
            if not (0 <= e.offset <= ui_len and 0 <= e.length and e.offset + e.length <= ui_len):
                raise ValueError(
                    f"Entity out of bounds (UI): offset={e.offset} length={e.length} for UI text len {ui_len}")

        # 2) затем нормализуем offsets/length в питоновские индексы
        norm = _normalize_entities_from_ui_to_py(txt, entities)

        # 3) финальная проверка уже в питон-метрике (защита от артефактов)
        py_len = len(txt)
        for e in norm:
            if not (0 <= e.offset <= py_len and 0 <= e.length and e.offset + e.length <= py_len):
                raise ValueError(
                    f"Entity out of bounds (PY): offset={e.offset} length={e.length} for text len {py_len}")

        return norm
