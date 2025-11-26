"""Конвертер Textile в BBCode.

Предоставляет функцию высокого уровня ``convert`` для преобразования
Textile-разметки в BBCode. Логика преобразования держится максимально
простой и пригодной для CLI-обёртки.
"""
from __future__ import annotations

import re


CODE_BLOCK_PATTERN = re.compile(
    r"<pre><code(?: class=\"([^\"]+)\")?>\s*(.*?)\s*</code></pre>",
    re.IGNORECASE | re.DOTALL,
)
HEADING_PATTERN = re.compile(r"^h([1-6])\.\s+(.*)$")
INLINE_CODE_PATTERN = re.compile(r"@(.*?)@")
LIST_MARKERS = {"#": "[list=1]", "*": "[list]"}
HEADING_SIZES = {
    "1": "18pt",
    "2": "16pt",
    "3": "14pt",
    "4": "12pt",
    "5": "10pt",
    "6": "8pt",
}


def _replace_code_blocks(text: str) -> str:
    """Заменяет блочные конструкции ``<pre><code>`` на BBCode.

    Возвращает обновлённый текст, в котором блоки кода превращены в
    ``[code]`` с указанием языка, если он был задан в классе ``code``.
    """

    def _to_bbcode(match: re.Match[str]) -> str:
        language, body = match.groups()
        language_suffix = f"={language.lower()}" if language else ""
        cleaned_body = body.strip("\n")
        escaped_header = _escape_bbcode(f"[code{language_suffix}]")
        escaped_footer = _escape_bbcode("[/code]")
        return "\n".join(["[CODE]", escaped_header, cleaned_body, escaped_footer, "[/CODE]"])

    return CODE_BLOCK_PATTERN.sub(_to_bbcode, text)


def _convert_inline_code(text: str) -> str:
    """Преобразует инлайн-конструкции ``@код@`` в BBCode ``[code]``."""

    return INLINE_CODE_PATTERN.sub(lambda m: f"[code]{m.group(1)}[/code]", text)


def _escape_bbcode(text: str) -> str:
    """Экранирует квадратные скобки, чтобы BBCode не парсился внутри ``[CODE]``."""

    return text.replace("[", "&#91;").replace("]", "&#93;")


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
        size = HEADING_SIZES.get(level, "12pt")
        text = title.strip()
        return f"[SIZE={size}][B]{text}[/B][/SIZE]"

    return _convert_inline_code(line)


def _close_list_stack(lines: list[str], stack: list[str]) -> None:
    """Закрывает все уровни вложенных списков."""

    while stack:
        closing = _close_list(stack.pop())
        if closing:
            lines.append(closing)


def _sync_list_levels(lines: list[str], stack: list[str], markers: str) -> None:
    """Синхронизирует активные уровни списков с текущими маркерами."""

    new_levels = list(markers)

    while len(stack) > len(new_levels):
        closing = _close_list(stack.pop())
        if closing:
            lines.append(closing)

    for idx, marker in enumerate(new_levels):
        if idx >= len(stack) or stack[idx] != marker:
            while len(stack) > idx:
                closing = _close_list(stack.pop())
                if closing:
                    lines.append(closing)
            lines.append(_start_list(marker))
            stack.append(marker)


def convert(text: str) -> str:
    """Конвертирует Textile-строку в BBCode.

    Поддерживаемые элементы:
    * Заголовки ``h1.`` – ``h6.`` → ``[SIZE=NNpt][B]...[/B][/SIZE]``
      (18pt для ``h1`` и далее по убыванию).
    * Инлайн-код ``@...@`` → ``[code]``.
    * Блоки ``<pre><code class="lang">`` → ``[CODE]`` с экранированным
      содержимым ``[code]`` и ``[/code]``.
    * Маркированные и нумерованные списки на основе ``*`` и ``#``.
    Остальной текст остаётся без изменений.
    """

    text = _replace_code_blocks(text)
    converted_lines: list[str] = []
    list_stack: list[str] = []

    for raw_line in text.splitlines():
        list_match = re.match(r"^([#*]+)\s+(.*)$", raw_line)
        if list_match:
            markers, content = list_match.groups()
            _sync_list_levels(converted_lines, list_stack, markers)
            converted_lines.append(f"[*]{_convert_inline_code(content.strip())}")
            continue

        if list_stack and raw_line.strip():
            converted_lines[-1] = "\n".join(
                [converted_lines[-1], _convert_inline_code(raw_line.strip())]
            )
            continue

        if list_stack and not raw_line.strip():
            _close_list_stack(converted_lines, list_stack)
            continue

        converted_lines.append(_convert_line(raw_line))

    _close_list_stack(converted_lines, list_stack)
    return "\n".join(filter(lambda line: line is not None, converted_lines))


__all__ = ["convert"]
