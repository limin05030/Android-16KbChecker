# -*- coding: utf-8 -*-
# Author: sens
# Date: 2026/4/16 17:42
import os
import sys
import shutil

from android_sdk import get_llvm_objdump_path
from model import SoInfo
from prehandler import get_so_files
from so_analyze import so_analyze

# main.py 中不要出现中文，否则用stickytape导出后的代码存在编码问题。
# 用stickytape工具可以将所有代码打包成一个py文件
# 安装：pip install stickytape
# 使用：stickytape main.py --python-binary .venv/Scripts/python --output build/16KbChecker.py
# output目录需要自己手动创建
# 可进一步编译成pyc：python -m compileall -b build/16KbChecker.py
# 最低支持运行版本：3.10
# pip freeze > requirements.txt
# pip install -r requirements.txt
#
# pip install pyinstaller
# pyinstaller -F -n 16KbChecker main.py
def dump_result(abi_info: dict[str, list[SoInfo]]) -> None:
    """打印结果信息"""

    # 找出so名字最长的长度
    _so_name_max_len = 0
    for abi_name in abi_info:
        _so_list = abi_info[abi_name]
        for so_info in _so_list:
            _so_name_len = len(so_info.so_name)
            if _so_name_len > _so_name_max_len:
                _so_name_max_len = _so_name_len

    # 打印so信息
    first_column_width = _so_name_max_len  # 第一列宽度（不包含左右的一个空格）
    second_column_width = 4                # 第二列宽度（不包含左右的一个空格）
    print(f"┌─{'─' * first_column_width}───{'─' * second_column_width}─┐")
    for abi_index, abi_name in enumerate(abi_info):
        _so_list = abi_info[abi_name]
        print(f"│ ABI: {abi_name}{' ' * ((first_column_width + 2 + second_column_width + 2 + 1) - (5 + len(abi_name)) - 2)} │")
        print(f"├─{'─' * _so_name_max_len}─┬─{'─' * second_column_width}─┤")
        for index, so_info in enumerate(_so_list):
            if so_info.align >= 14:
                print(f"│ {so_info.so_name.ljust(_so_name_max_len)} │ {' ' * ((second_column_width - 4) // 2)}16Kb{' ' * ((second_column_width - 4) // 2)} │")
            else:
                print(f"│ {so_info.so_name.ljust(_so_name_max_len)} │ {' ' * second_column_width} │")
            if index == len(_so_list) - 1:
                if abi_index == len(abi_info) - 1:
                    print(f"└─{'─' * _so_name_max_len}─┴─{'─' * second_column_width}─┘")
                else:
                    print(f"├─{'─' * _so_name_max_len}─┴─{'─' * second_column_width}─┤")
            else:
                print(f"├─{'─' * _so_name_max_len}─┼─{'─' * second_column_width}─┤")

def run(file_path):
    if not os.path.exists(file_path):
        print(f"<{file_path}> not exists.")
        sys.exit(0)

    file_info = get_so_files(file_path)
    if not file_info:
        sys.exit(0)

    if len(file_info.so_list) == 0:
        print(".so file not found.")
        sys.exit(0)

    llvm_objdump = get_llvm_objdump_path()
    if not llvm_objdump:
        sys.exit(0)

    result = so_analyze(llvm_objdump, os_files=file_info.so_list)
    dump_result(result)

    if file_info.unzip_dir:
        shutil.rmtree(file_info.unzip_dir)