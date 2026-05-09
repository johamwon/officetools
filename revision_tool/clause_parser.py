# Copyright (c) 2026 王刚. All rights reserved.
import re
from dataclasses import dataclass, field


@dataclass
class Clause:
    number: str
    chapter: str = ""
    section: str = ""
    full_name: str = ""


_CN_NUM_MAP = {
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15,
    "十六": 16, "十七": 17, "十八": 18, "十九": 19, "二十": 20,
}

_PATTERNS = [
    re.compile(r"第[一二三四五六七八九十百千\d]+章"),
    re.compile(r"第[一二三四五六七八九十百千\d]+节"),
    re.compile(r"第[一二三四五六七八九十百千\d]+条"),
    re.compile(r"[（(][一二三四五六七八九十\d]+[）)]"),
    re.compile(r"^[一二三四五六七八九十]+[、．.]"),
    re.compile(r"^\d+[、．.\s]"),
]


def _cn_to_arabic(cn: str) -> int:
    cn = cn.strip()
    if cn in _CN_NUM_MAP:
        return _CN_NUM_MAP[cn]
    if "十" in cn:
        parts = cn.split("十")
        tens = _CN_NUM_MAP.get(parts[0], 1) if parts[0] else 1
        ones = _CN_NUM_MAP.get(parts[1], 0) if len(parts) > 1 and parts[1] else 0
        return tens * 10 + ones
    try:
        return int(cn)
    except ValueError:
        return 0


class ClauseParser:
    def __init__(self):
        self._current_chapter = ""
        self._current_section = ""

    def reset(self):
        self._current_chapter = ""
        self._current_section = ""

    def parse_paragraph(self, text: str) -> Clause | None:
        if not text or not text.strip():
            return None

        text = text.strip()

        chapter_match = re.match(r"第([一二三四五六七八九十百千\d]+)章", text)
        if chapter_match:
            self._current_chapter = f"第{chapter_match.group(1)}章"
            self._current_section = ""
            return Clause(
                number="",
                chapter=self._current_chapter,
                full_name=self._current_chapter,
            )

        section_match = re.match(r"第([一二三四五六七八九十百千\d]+)节", text)
        if section_match:
            self._current_section = f"第{section_match.group(1)}节"
            return Clause(
                number="",
                chapter=self._current_chapter,
                section=self._current_section,
                full_name=f"{self._current_chapter}{self._current_section}",
            )

        article_match = re.match(r"第([一二三四五六七八九十百千\d]+)条", text)
        if article_match:
            article_name = f"第{article_match.group(1)}条"
            parts = []
            if self._current_chapter:
                parts.append(self._current_chapter)
            if self._current_section:
                parts.append(self._current_section)
            parts.append(article_name)
            return Clause(
                number=article_name,
                chapter=self._current_chapter,
                section=self._current_section,
                full_name="".join(parts),
            )

        for pattern in _PATTERNS[3:]:
            if pattern.match(text):
                m = pattern.match(text)
                sub_number = m.group(0)
                parent = ""
                if self._current_chapter:
                    parent = self._current_chapter
                    if self._current_section:
                        parent += self._current_section
                full = f"{parent}{sub_number}" if parent else sub_number
                return Clause(number=sub_number, chapter=self._current_chapter,
                              section=self._current_section, full_name=full)

        return None

    def find_clause_for_text(self, text: str, context_paragraphs: list[str] | None = None) -> Clause | None:
        clause = self.parse_paragraph(text)
        if clause and clause.number:
            return clause

        if context_paragraphs:
            last_clause = None
            for para_text in context_paragraphs:
                c = self.parse_paragraph(para_text)
                if c and c.number:
                    last_clause = c
            if last_clause:
                return last_clause

        return None
