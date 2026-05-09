# Copyright (c) 2026 王刚. All rights reserved.
from dataclasses import dataclass
from copy import deepcopy

from lxml import etree
from docx import Document


NSMAP = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
}

W_NS = NSMAP["w"]


def _qn(tag: str) -> str:
    prefix, local = tag.split(":")
    return f"{{{NSMAP[prefix]}}}{local}"


@dataclass
class Revision:
    paragraph_index: int
    clause_name: str
    deleted_text: str
    inserted_text: str
    context_before: str = ""
    context_after: str = ""


def _get_text_from_runs(element) -> str:
    texts = []
    for t in element.iter(_qn("w:t")):
        if t.text:
            texts.append(t.text)
    return "".join(texts)


def _get_deleted_text(element) -> str:
    texts = []
    for t in element.iter(_qn("w:delText")):
        if t.text:
            texts.append(t.text)
    if texts:
        return "".join(texts)
    for t in element.iter(_qn("w:t")):
        if t.text:
            texts.append(t.text)
    return "".join(texts)


def _extract_paragraph_text_without_revisions(para_element) -> str:
    texts = []
    for child in para_element:
        tag = child.tag
        if tag == _qn("w:r"):
            for t in child.iter(_qn("w:t")):
                if t.text:
                    texts.append(t.text)
        elif tag == _qn("w:ins"):
            pass
        elif tag == _qn("w:del"):
            pass
        elif tag in (_qn("w:pPr"), _qn("w:bookmarkStart"), _qn("w:bookmarkEnd")):
            pass
        else:
            texts.append(_get_text_from_runs(child))
    return "".join(texts)


def _extract_paragraph_accepted_text(para_element) -> str:
    texts = []
    for child in para_element:
        tag = child.tag
        if tag == _qn("w:r"):
            for t in child.iter(_qn("w:t")):
                if t.text:
                    texts.append(t.text)
        elif tag == _qn("w:ins"):
            for t in child.iter(_qn("w:t")):
                if t.text:
                    texts.append(t.text)
        elif tag == _qn("w:del"):
            pass
        elif tag in (_qn("w:pPr"), _qn("w:bookmarkStart"), _qn("w:bookmarkEnd")):
            pass
        else:
            texts.append(_get_text_from_runs(child))
    return "".join(texts)


def _extract_paragraph_rejected_text(para_element) -> str:
    texts = []
    for child in para_element:
        tag = child.tag
        if tag == _qn("w:r"):
            for t in child.iter(_qn("w:t")):
                if t.text:
                    texts.append(t.text)
        elif tag == _qn("w:ins"):
            pass
        elif tag == _qn("w:del"):
            texts.append(_get_deleted_text(child))
        elif tag in (_qn("w:pPr"), _qn("w:bookmarkStart"), _qn("w:bookmarkEnd")):
            pass
        else:
            texts.append(_get_text_from_runs(child))
    return "".join(texts)


def _has_revision_marks(para_element) -> bool:
    return bool(para_element.findall(_qn("w:ins"))) or bool(para_element.findall(_qn("w:del")))


def _merge_adjacent_revisions(revisions: list[Revision]) -> list[Revision]:
    if not revisions:
        return revisions
    merged = [revisions[0]]
    for rev in revisions[1:]:
        last = merged[-1]
        if (rev.paragraph_index == last.paragraph_index
                and not last.inserted_text
                and not rev.deleted_text
                and rev.clause_name == last.clause_name):
            last.inserted_text = rev.inserted_text
        elif (rev.paragraph_index == last.paragraph_index
              and rev.clause_name == last.clause_name):
            merged.append(rev)
        else:
            merged.append(rev)
    return merged


def extract_revisions(doc: Document) -> list[Revision]:
    revisions = []
    body = doc.element.body
    paragraphs = body.findall(_qn("w:p"))

    from .clause_parser import ClauseParser
    parser = ClauseParser()

    all_para_texts = []
    for p in paragraphs:
        all_para_texts.append(_extract_paragraph_accepted_text(p))

    parser.reset()
    for i, para in enumerate(paragraphs):
        if not _has_revision_marks(para):
            accepted = _extract_paragraph_accepted_text(para)
            parser.parse_paragraph(accepted)
            continue

        accepted_text = _extract_paragraph_accepted_text(para)
        rejected_text = _extract_paragraph_rejected_text(para)
        context = _extract_paragraph_text_without_revisions(para)

        clause = parser.find_clause_for_text(accepted_text, all_para_texts[:i])
        clause_name = clause.full_name if clause else ""

        del_texts = []
        for del_elem in para.findall(_qn("w:del")):
            del_texts.append(_get_deleted_text(del_elem))

        ins_texts = []
        for ins_elem in para.findall(_qn("w:ins")):
            ins_texts.append(_get_text_from_runs(ins_elem))

        if del_texts or ins_texts:
            rev = Revision(
                paragraph_index=i,
                clause_name=clause_name,
                deleted_text="".join(del_texts),
                inserted_text="".join(ins_texts),
                context_before=rejected_text,
                context_after=accepted_text,
            )
            revisions.append(rev)

        parser.parse_paragraph(accepted_text)

    revisions = _merge_adjacent_revisions(revisions)
    return revisions


def accept_all_revisions(doc: Document) -> Document:
    body = doc.element.body

    for del_elem in body.findall(f".//{_qn('w:del')}"):
        del_elem.getparent().remove(del_elem)

    for ins_elem in body.findall(f".//{_qn('w:ins')}"):
        parent = ins_elem.getparent()
        parent.remove(ins_elem)
        for child in list(ins_elem):
            if child.tag in (_qn("w:r"), _qn("w:hyperlink")):
                parent.append(child)

    for rpr_change in body.findall(f".//{_qn('w:rPrChange')}"):
        rpr = rpr_change.getparent()
        rpr.remove(rpr_change)

    for ppr_change in body.findall(f".//{_qn('w:pPrChange')}"):
        ppr = ppr_change.getparent()
        ppr.remove(ppr_change)

    for sectpr_change in body.findall(f".//{_qn('w:sectPrChange')}"):
        sectpr = sectpr_change.getparent()
        sectpr.remove(sectpr_change)

    for tblpr_change in body.findall(f".//{_qn('w:tblPrChange')}"):
        tblpr = tblpr_change.getparent()
        tblpr.remove(tblpr_change)

    for tcpr_change in body.findall(f".//{_qn('w:tcPrChange')}"):
        tcpr = tcpr_change.getparent()
        tcpr.remove(tcpr_change)

    for move_from in body.findall(f".//{_qn('w:moveFrom')}"):
        move_from.getparent().remove(move_from)

    for move_to in body.findall(f".//{_qn('w:moveTo')}"):
        parent = move_to.getparent()
        parent.remove(move_to)
        for child in list(move_to):
            parent.append(child)

    for move_from_r in body.findall(f".//{_qn('w:moveFromRangeStart')}"):
        move_from_r.getparent().remove(move_from_r)
    for move_from_r in body.findall(f".//{_qn('w:moveFromRangeEnd')}"):
        move_from_r.getparent().remove(move_from_r)
    for move_to_r in body.findall(f".//{_qn('w:moveToRangeStart')}"):
        move_to_r.getparent().remove(move_to_r)
    for move_to_r in body.findall(f".//{_qn('w:moveToRangeEnd')}"):
        move_to_r.getparent().remove(move_to_r)

    return doc
