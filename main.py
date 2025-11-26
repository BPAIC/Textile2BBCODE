"""CLI для конвертации Textile-файлов в BBCode."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import TextIO

from textile2bbcode.converter import convert


def _read_text(stream: TextIO) -> str:
    """Считывает весь текст из переданного потока."""

    return stream.read()


def _write_text(stream: TextIO, content: str) -> None:
    """Записывает контент в поток вывода."""

    stream.write(content)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Преобразует Textile-разметку в BBCode",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Путь к Textile-файлу для конвертации",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Путь к файлу для сохранения BBCode (по умолчанию stdout)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    with args.input.open("r", encoding="utf-8") as source:
        textile = _read_text(source)

    bbcode = convert(textile)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as target:
            _write_text(target, bbcode)
    else:
        _write_text(stream=open(1, "w", encoding="utf-8", closefd=False), content=bbcode)


if __name__ == "__main__":
    main()
