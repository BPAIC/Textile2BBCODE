"""Набор модульных тестов для конвертера Textile → BBCode."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from textile2bbcode.converter import convert


class ConvertTestCase(unittest.TestCase):
    """Проверяет корректность преобразования основных конструкций."""

    def test_heading_conversion(self) -> None:
        """Заголовки hN. превращаются в BBCode с указанным размером."""

        self.assertEqual(convert("h1. Заголовок"), "[SIZE=18pt][B]Заголовок[/B][/SIZE]")

    def test_inline_code_conversion(self) -> None:
        """Инлайн-код оборачивается тегами [code]."""

        self.assertEqual(convert("Используйте @print@"), "Используйте [code]print[/code]")

    def test_code_block_with_language(self) -> None:
        """Блочный код сохраняет язык и экранирует вложенные теги."""

        source = "<pre><code class=\"python\">\nprint('hi')\n</code></pre>"
        expected = "\n".join(
            [
                "[CODE]",
                "&#91;code=python&#93;",
                "print('hi')",
                "&#91;/code&#93;",
                "[/CODE]",
            ]
        )
        self.assertEqual(convert(source), expected)

    def test_nested_list_synchronization(self) -> None:
        """Списки корректно открываются и закрываются при смене уровней."""

        source = "\n".join(
            [
                "# Первый",
                "## Вложенный",
                "# Второй",
                "",
                "Продолжение",
            ]
        )
        expected = "\n".join(
            [
                "[list=1]",
                "[*]Первый",
                "[list=1]",
                "[*]Вложенный",
                "[/list]",
                "[*]Второй",
                "[/list]",
                "Продолжение",
            ]
        )
        self.assertEqual(convert(source), expected)


if __name__ == "__main__":
    unittest.main()
