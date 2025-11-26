"""Конвертер Textile в BBCode.

Предоставляет функцию высокого уровня ``convert`` для преобразования
Textile-разметки в BBCode. Логика преобразования держится максимально
простой и пригодной для CLI-обёртки.
"""
from __future__ import annotations

import re
from typing import Iterable


CODE_BLOCK_PATTERN = re.compile(
    r"<pre><code(?: class=\"([^\"]+)\")?>\s*(.*?)\s*</code></pre>",
    re.IGNORECASE | re.DOTALL,
)
HEADING_PATTERN = re.compile(r"^h([1-6])\.\s+(.*)$")
INLINE_CODE_PATTERN = re.compile(r"@(.*?)@")
LIST_MARKERS = {"#": "[list=1]", "*": "[list]"}


def _replace_code_blocks(text: str) -> str:
    """Заменяет блочные конструкции ``<pre><code>`` на BBCode.

    Возвращает обновлённый текст, в котором блоки кода превращены в
    ``[code]`` с указанием языка, если он был задан в классе ``code``.
    """

    def _to_bbcode(match: re.Match[str]) -> str:
        language, body = match.groups()
        language_suffix = f"={language.lower()}" if language else ""
        cleaned_body = body.strip("\n")
        return f"[code{language_suffix}]\n{cleaned_body}\n[/code]"

    return CODE_BLOCK_PATTERN.sub(_to_bbcode, text)


def _convert_inline_code(text: str) -> str:
    """Преобразует инлайн-конструкции ``@код@`` в BBCode ``[code]``."""

    return INLINE_CODE_PATTERN.sub(lambda m: f"[code]{m.group(1)}[/code]", text)


def _start_list(marker: str) -> str:
    """Возвращает BBCode-открывающий тег для списка."""

    return LIST_MARKERS.get(marker, "[list]")


def _close_list(active: str | None) -> str | None:
    """Возвращает закрывающий тег списка, если он активен."""

    return "[/list]" if active else None


def _convert_line(line: str) -> str:
    """Преобразует одиночную строку без учёта списков."""

    heading_match = HEADING_PATTERN.match(line)
    if heading_match:
        level, title = heading_match.groups()
        return f"[h{level}]{title.strip()}[/h{level}]"

    return _convert_inline_code(line)


def _finalize_result(lines: Iterable[str], active_list: str | None) -> list[str]:
    """Добавляет закрытие списка, если необходимо."""

    if active_list:
        lines.append(_close_list(active_list))
    return list(lines)


def convert(text: str) -> str:
    """Конвертирует Textile-строку в BBCode.

    Поддерживаемые элементы:
    * Заголовки ``h1.`` – ``h6.`` → ``[hX]``.
    * Инлайн-код ``@...@`` → ``[code]``.
    * Блоки ``<pre><code class="lang">`` → ``[code=lang]``.
    * Маркированные и нумерованные списки на основе ``*`` и ``#``.
    Остальной текст остаётся без изменений.
    """

    text = _replace_code_blocks(text)
    converted_lines: list[str] = []
    active_list: str | None = None

    for raw_line in text.splitlines():
        list_match = re.match(r"^([#*])\s+(.*)$", raw_line)
        if list_match:
            marker, content = list_match.groups()
            if active_list != marker:
                if active_list:
                    closing = _close_list(active_list)
                    if closing:
                        converted_lines.append(closing)
                converted_lines.append(_start_list(marker))
                active_list = marker
            converted_lines.append(f"[*]{_convert_inline_code(content.strip())}")
            continue

        if active_list:
            closing = _close_list(active_list)
            if closing:
                converted_lines.append(closing)
            active_list = None

        converted_lines.append(_convert_line(raw_line))

    finalized = _finalize_result(converted_lines, active_list)
    return "\n".join(filter(lambda line: line is not None, finalized))


__all__ = ["convert"]
