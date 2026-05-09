# Copyright (c) 2026 王刚. All rights reserved.
import sys
import click
from revision_tool.core import RevisionTool

COPYRIGHT = "Copyright (c) 2026 王刚. All rights reserved."


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """制度修订对照表自动生成工具

    Copyright (c) 2026 王刚. All rights reserved.
    """
    if ctx.invoked_subcommand is None:
        from revision_tool.gui import run_gui
        run_gui()


@cli.command()
@click.argument("doc_path", type=click.Path(exists=True))
@click.option("-o", "--output", "output_path", default=None, help="输出文件路径")
@click.option("--accept/--no-accept", "accept_changes", default=True,
              help="是否接受所有修订 (默认接受)")
@click.option("-p", "--position", "table_position", default="end",
              type=click.Choice(["end", "start", "before_body", "marker"]),
              help="对照表插入位置")
@click.option("-m", "--marker", "marker_text", default="",
              help="当position=marker时，对照表插入到包含此文本的段落之前")
def tracked(doc_path, output_path, accept_changes, table_position, marker_text):
    """处理带修订痕迹的单个文档"""
    tool = RevisionTool()
    revisions = tool.process_tracked_changes(
        doc_path=doc_path,
        output_path=output_path,
        accept_changes=accept_changes,
        table_position=table_position,
        marker_text=marker_text,
    )
    tool.print_summary(revisions)


@cli.command()
@click.argument("old_doc_path", type=click.Path(exists=True))
@click.argument("new_doc_path", type=click.Path(exists=True))
@click.option("-o", "--output", "output_path", default=None, help="输出文件路径")
@click.option("-p", "--position", "table_position", default="end",
              type=click.Choice(["end", "start", "before_body", "marker"]),
              help="对照表插入位置")
@click.option("-m", "--marker", "marker_text", default="",
              help="当position=marker时，对照表插入到包含此文本的段落之前")
def compare(old_doc_path, new_doc_path, output_path, table_position, marker_text):
    """对比两个文档并生成修订对照表"""
    tool = RevisionTool()
    revisions = tool.process_two_docs(
        old_doc_path=old_doc_path,
        new_doc_path=new_doc_path,
        output_path=output_path,
        table_position=table_position,
        marker_text=marker_text,
    )
    tool.print_summary(revisions)


@cli.command()
@click.argument("doc_path", type=click.Path(exists=True))
@click.option("-o", "--output", "output_path", default="revision_table.docx",
              help="对照表输出路径")
def table_only(doc_path, output_path):
    """仅从带修订痕迹的文档中提取对照表（不修改原文档）"""
    tool = RevisionTool()
    from docx import Document
    from revision_tool.tracked_changes import extract_revisions

    doc = Document(doc_path)
    revisions = extract_revisions(doc)
    tool.revisions = revisions
    tool.generate_table_only(revisions, output_path)
    tool.print_summary(revisions)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        from revision_tool.gui import run_gui
        run_gui()
    else:
        cli()
