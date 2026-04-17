# -*- coding: utf-8 -*-
# Author: sens
# Date: 2026/4/16 15:53
import os
import tempfile
import zipfile

from model import FileInfo


def __unzip(zip_path) -> str:
    _unzip_temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            # 将目标目录与成员路径拼接后，检查是否仍在 extract_path 内
            _abs_path = os.path.join(os.path.abspath(_unzip_temp_dir), member)
            if not os.path.abspath(_abs_path).startswith(os.path.abspath(_unzip_temp_dir)):
                raise Exception(f"检测到路径遍历攻击: {member}")
        zip_ref.extractall(_unzip_temp_dir)

    return _unzip_temp_dir

def __find_so_files(file_path) -> list[str]:
    if not os.path.exists(file_path):
        return []

    if os.path.isfile(file_path):
        return [file_path] if file_path.endswith(".so") else []
    elif os.path.isdir(file_path):
        _os_files = []
        for f in os.listdir(file_path):
            _os_files.extend(__find_so_files(os.path.join(file_path, f)))
        return _os_files
    else:
        return []

def get_so_files(file_path) -> FileInfo | None:
    """从 file_path 中获取os文件"""

    if not os.path.exists(file_path):
        print(f"<{file_path}> not exists.")
        return None

    _unzip_dir: str | None = None
    _so_files: list[str] = []

    print("collect .so files...")
    if os.path.isfile(file_path):
        if file_path.endswith(".apk"):
            _unzip_dir = __unzip(file_path)
            _lib_dir = os.path.join(_unzip_dir, "lib")
            if not os.path.isdir(_lib_dir):
                _lib_dir = _unzip_dir
            _so_files = __find_so_files(_lib_dir)
        elif file_path.endswith(".aab"):
            _unzip_dir = __unzip(file_path)
            _lib_dir = os.path.join(_unzip_dir, "base", "lib")
            if not os.path.isdir(_lib_dir):
                _lib_dir = _unzip_dir
            _so_files = __find_so_files(_lib_dir)
        elif file_path.endswith(".so"):
            _so_files = __find_so_files(file_path)
        else:
            print(f"<{file_path}> is a invalid path.")
            return None
    elif os.path.isdir(file_path):
        _so_files = __find_so_files(file_path)
    else:
        print(f"<{file_path}> is a invalid path.")
        return None

    return FileInfo(file_path=file_path, unzip_dir=_unzip_dir, so_list=_so_files)
