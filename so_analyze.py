# -*- coding: utf-8 -*-
# Author: sens
# Date: 2026/4/16 15:22
import os
import sys
import traceback

from elftools.elf.elffile import ELFFile
from model import SoInfo
from utils import exec_cmd

# 工具支持的abi类型
supported_abis = ["armeabi-v7a", "arm64-v8a", "x86", "x86_64"]

# 使用ELFFile库获取到的so文件的abi类型的映射关系
abi_maps = {
    "EM_ARM": "armeabi-v7a",
    "EM_AARCH64": "arm64-v8a",
    "EM_386": "x86",
    "EM_X86_64": "x86_64",
}

def __get_so_abi(so_path: str) -> str | None:
    # noinspection PyBroadException
    try:
        with open(so_path, 'rb') as f:
            _elf = ELFFile(f)
            _arch = _elf.header.e_machine
            return abi_maps[_arch]
    except Exception:
        traceback.print_exc()

    return None

def so_analyze(llvm_objdump: str, os_files: list[str]) -> dict[str, list[SoInfo]] | None:
    """分析so文件是否支持 16kb size"""
    print("analyze .so files...")

    _filter_cmd = "findstr" if sys.platform.startswith("win") else "grep"

    _check_result = {}
    for _os_file in os_files:
        _code, _data = exec_cmd(f"\"{llvm_objdump}\" -p \"{_os_file}\" | {_filter_cmd} \"LOAD\"")
        if _code != 0 or not _data:
            print("Error:", _code, _data)
            return None

        _lines = _data.splitlines()
        _min_align = 999
        for _line in _lines:
            try:
                _align = int(_line[-2:])
                if _align < _min_align:
                    _min_align = _align
            except ValueError:
                print(_lines)
                print("Error: cannot parse align number")
                return None

        _abi = __get_so_abi(_os_file) or "N/A"
        _so_list = _check_result.setdefault(_abi, [])
        _so_list.append(SoInfo(_abi, os.path.basename(_os_file), _min_align))

    return _check_result