# officetools

制度修订对照表自动生成工具，用于处理 Word 文档（`.docx`）中的修订内容并生成对照表。

## 功能

- 处理带修订痕迹的单个文档并插入修订对照表
- 对比旧版与新版文档并在新文档中插入修订对照表
- 仅生成修订对照表文档（不修改原文档）
- 支持命令行与图形界面（直接运行默认进入 GUI）

## 环境要求

- Python 3.10+
- 依赖见 `requirements.txt`

## 安装

```bash
pip install -r requirements.txt
```

## 使用方式

### 1) 直接启动（默认 GUI）

```bash
python main.py
```

### 2) 处理单个带修订文档

```bash
python main.py tracked <doc_path> [-o 输出路径] [--accept/--no-accept] [-p end|start|before_body|marker] [-m 标记文本]
```

### 3) 对比两个文档并生成修订对照表

```bash
python main.py compare <old_doc_path> <new_doc_path> [-o 输出路径] [-p end|start|before_body|marker] [-m 标记文本]
```

### 4) 仅导出修订对照表

```bash
python main.py table-only <doc_path> [-o 输出路径]
```

## 打包（可选）

仓库提供了 `build.py` 与 `revision_tool.spec`，可用于生成可执行文件：

```bash
python build.py --clean
```