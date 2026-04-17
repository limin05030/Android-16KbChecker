# -*- coding: utf-8 -*-
# Author: sens
# Date: 2026/4/16 15:22
import os
import sys
import traceback

# pyelftools
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
    try:
        with open(so_path, 'rb') as f:
            elf = ELFFile(f)
            # 获取机器架构
            arch = elf.header.e_machine
            # 获取文件类型
            file_type = elf.header.e_type
            # 获取 ELF 位数
            elf_class = elf.header['e_ident']['EI_CLASS']

            # print(f"文件架构: {arch}")
            # print(f"文件类型: {file_type} (共享库: 'ET_DYN')")
            # print(f"ELF 位数: {elf_class} (32位: 'ELFCLASS32', 64位: 'ELFCLASS64')")

            # 可选：进一步解析 ELF 信息
            # ... 参考 `pyelftools` 文档获取更多信息

            return abi_maps[arch]
    except Exception:
        # print(f"读取文件 {file_path} 时出错: {e}")
        traceback.print_exc()

    return None

def so_analyze(llvm_objdump: str, os_files: list[str]) -> dict[str, list[SoInfo]]:
    """分析so文件是否支持 16kb size"""
    print("analyze .so files...")

    check_result = {}
    for os_file in os_files:
        abi = __get_so_abi(os_file) or "N/A"

        if sys.platform.startswith("win"):
            code, data = exec_cmd(f"\"{llvm_objdump}\" -p \"{os_file}\" | findstr \"LOAD\"")
        else:
            code, data = exec_cmd(f"\"{llvm_objdump}\" -p \"{os_file}\" | grep \"LOAD\"")

        if code != 0:
            print(data)
            exit(0)

        lines = data.split("\n")
        min_align = 999
        for line in lines:
            try:
                align = int(line[-2:])
                if align < min_align:
                    min_align = align
            except ValueError:
                print(lines)
                print("cannot parse align number")
                exit(0)

        so_list = check_result.get(abi)
        if so_list is None:
            so_list = []
            check_result[abi] = so_list
        so_list.append(SoInfo(abi, os.path.basename(os_file), min_align))

    return check_result