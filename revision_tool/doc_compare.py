# Copyright (c) 2026 王刚. All rights reserved.
import difflib
from dataclasses import dataclass
from docx import Document

from .tracked_changes import Revision
from .clause_parser import ClauseParser


@dataclass
class ParagraphBlock:
    index: int
    text: str
    clause_name: str = ""


def _extract_paragraphs(doc: Document) -> list[str]:
    return [p.text for p in doc.paragraphs]


def _normalize_text(text: str) -> str:
    return text.strip().replace("\r\n", "\n").replace("\r", "\n")


def compare_documents(old_doc: Document, new_doc: Document) -> list[Revision]:
    old_paras = [_normalize_text(p) for p in _extract_paragraphs(old_doc)]
    new_paras = [_normalize_text(p) for p in _extract_paragraphs(new_doc)]

    old_filtered = [(i, t) for i, t in enumerate(old_paras) if t]
    new_filtered = [(i, t) for i, t in enumerate(new_paras) if t]

    old_texts = [t for _, t in old_filtered]
    new_texts = [t for _, t in new_filtered]

    old_parser = ClauseParser()
    for t in old_texts:
        old_parser.parse_paragraph(t)

    new_parser = ClauseParser()
    for t in new_texts:
        new_parser.parse_paragraph(t)

    revisions = []
    parser = ClauseParser()
    processed_new_indices = set()

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            for k in range(j1, j2):
                parser.parse_paragraph(new_texts[k])
            continue

        if tag == "replace":
            old_block = "\n".join(old_texts[i1:i2])
            new_block = "\n".join(new_texts[j1:j2])

            for k in range(j1, j2):
                clause = parser.find_clause_for_text(
                    new_texts[k],
                    new_texts[:k] if k > 0 else None,
                )
                if not clause:
                    parser.parse_paragraph(new_texts[k])
                    clause = parser.find_clause_for_text(new_texts[k])

                clause_name = clause.full_name if clause else ""

                old_for_clause = "\n".join(old_texts[i1:i2])
                new_for_clause = new_texts[k]

                rev = Revision(
                    paragraph_index=new_filtered[k][0],
                    clause_name=clause_name,
                    deleted_text=old_for_clause,
                    inserted_text=new_for_clause,
                    context_before=old_for_clause,
                    context_after=new_for_clause,
                )
                revisions.append(rev)
                processed_new_indices.add(k)
                parser.parse_paragraph(new_texts[k])

        elif tag == "insert":
            for k in range(j1, j2):
                clause = parser.find_clause_for_text(
                    new_texts[k],
                    new_texts[:k] if k > 0 else None,
                )
                if not clause:
                    parser.parse_paragraph(new_texts[k])
                    clause = parser.find_clause_for_text(new_texts[k])

                clause_name = clause.full_name if clause else ""

                rev = Revision(
                    paragraph_index=new_filtered[k][0],
                    clause_name=clause_name,
                    deleted_text="",
                    inserted_text=new_texts[k],
                    context_before="（新增）",
                    context_after=new_texts[k],
                )
                revisions.append(rev)
                processed_new_indices.add(k)
                parser.parse_paragraph(new_texts[k])

        elif tag == "delete":
            for k in range(i1, i2):
                old_parser_single = ClauseParser()
                for prev_t in old_texts[:k]:
                    old_parser_single.parse_paragraph(prev_t)
                clause = old_parser_single.find_clause_for_text(old_texts[k], old_texts[:k])
                clause_name = clause.full_name if clause else ""

                rev = Revision(
                    paragraph_index=old_filtered[k][0],
                    clause_name=clause_name,
                    deleted_text=old_texts[k],
                    inserted_text="",
                    context_before=old_texts[k],
                    context_after="（删除）",
                )
                revisions.append(rev)

    return revisions


def compare_documents_inline(old_doc: Document, new_doc: Document) -> list[Revision]:
    old_paras = [_normalize_text(p) for p in _extract_paragraphs(old_doc)]
    new_paras = [_normalize_text(p) for p in _extract_paragraphs(new_doc)]

    old_filtered = [(i, t) for i, t in enumerate(old_paras) if t]
    new_filtered = [(i, t) for i, t in enumerate(new_paras) if t]

    old_texts = [t for _, t in old_filtered]
    new_texts = [t for _, t in new_filtered]

    revisions = []
    parser = ClauseParser()

    matcher = difflib.SequenceMatcher(None, old_texts, new_texts, autojunk=False)
    opcodes = matcher.get_opcodes()

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "equal":
            for k in range(j1, j2):
                parser.parse_paragraph(new_texts[k])
            continue

        if tag == "replace":
            old_strs = old_texts[i1:i2]
            new_strs = new_texts[j1:j2]
            max_len = max(len(old_strs), len(new_strs))

            for k in range(max_len):
                old_t = old_strs[k] if k < len(old_strs) else ""
                new_t = new_strs[k] if k < len(new_strs) else ""

                if new_t:
                    clause = parser.find_clause_for_text(new_t, new_texts[:j1 + k])
                    clause_name = clause.full_name if clause else ""
                    parser.parse_paragraph(new_t)
                elif old_t:
                    clause = parser.find_clause_for_text(old_t, old_texts[:i1 + k])
                    clause_name = clause.full_name if clause else ""
                else:
                    clause_name = ""

                rev = Revision(
                    paragraph_index=new_filtered[j1 + k][0] if k < len(new_strs) else -1,
                    clause_name=clause_name,
                    deleted_text=old_t,
                    inserted_text=new_t,
                    context_before=old_t,
                    context_after=new_t,
                )
                revisions.append(rev)

        elif tag == "insert":
            for k in range(j1, j2):
                clause = parser.find_clause_for_text(new_texts[k], new_texts[:k])
                clause_name = clause.full_name if clause else ""
                parser.parse_paragraph(new_texts[k])

                rev = Revision(
                    paragraph_index=new_filtered[k][0],
                    clause_name=clause_name,
                    deleted_text="",
                    inserted_text=new_texts[k],
                    context_before="（新增）",
                    context_after=new_texts[k],
                )
                revisions.append(rev)

        elif tag == "delete":
            for k in range(i1, i2):
                old_parser_single = ClauseParser()
                for prev_t in old_texts[:k]:
                    old_parser_single.parse_paragraph(prev_t)
                clause = old_parser_single.find_clause_for_text(old_texts[k], old_texts[:k])
                clause_name = clause.full_name if clause else ""

                rev = Revision(
                    paragraph_index=old_filtered[k][0],
                    clause_name=clause_name,
                    deleted_text=old_texts[k],
                    inserted_text="",
                    context_before=old_texts[k],
                    context_after="（删除）",
                )
                revisions.append(rev)

    return revisions
