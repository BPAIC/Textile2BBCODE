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


def _resolve_txt_output(input_path: Path, txt_output: Path | None) -> Path:
    """Возвращает путь для TXT-результата с гарантированным расширением."""

    if txt_output:
        target = txt_output
    else:
        target = input_path.with_suffix(".txt")

    if target.suffix.lower() != ".txt":
        target = target.with_suffix(".txt")

    target.parent.mkdir(parents=True, exist_ok=True)
    return target


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
    parser.add_argument(
        "--save-txt",
        dest="txt_output",
        nargs="?",
        const=None,
        type=Path,
        help=(
            "Сохранить результат в TXT. Без аргумента файл появится рядом с входным"
        ),
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
    elif args.txt_output is not None:
        txt_path = _resolve_txt_output(args.input, args.txt_output)
        with txt_path.open("w", encoding="utf-8") as target:
            _write_text(target, bbcode)
    else:
        _write_text(stream=open(1, "w", encoding="utf-8", closefd=False), content=bbcode)


if __name__ == "__main__":
    main()
