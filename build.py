# Copyright (c) 2026 王刚. All rights reserved.
import subprocess
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SPEC_FILE = PROJECT_ROOT / "revision_tool.spec"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def check_pyinstaller():
    try:
        import PyInstaller
        print(f"PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("未安装 PyInstaller，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def clean():
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"已清理: {d}")


def build():
    print("=" * 50)
    print("开始打包：制度修订对照表生成工具")
    print("=" * 50)

    check_pyinstaller()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(SPEC_FILE),
    ]
    print(f"\n执行: {' '.join(cmd)}\n")
    subprocess.check_call(cmd)

    exe_path = DIST_DIR / "制度修订对照表生成工具.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n{'=' * 50}")
        print(f"打包成功！")
        print(f"输出文件: {exe_path}")
        print(f"文件大小: {size_mb:.1f} MB")
        print(f"{'=' * 50}")
    else:
        print("\n打包失败：未找到输出文件")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="打包构建脚本")
    parser.add_argument("--clean", action="store_true", help="清理构建目录后重新打包")
    args = parser.parse_args()

    if args.clean:
        clean()
    build()
