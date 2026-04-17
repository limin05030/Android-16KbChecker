# -*- coding: utf-8 -*-
# Author: sens
# Date: 2026/4/16 15:51

class FileInfo:

    def __init__(self, file_path: str, unzip_dir: str | None, so_list: list[str]):
        self.file_path = file_path
        self.unzip_dir = unzip_dir
        self.so_list = so_list

class SoInfo:

    def __init__(self, abi_name: str, so_name: str, align: int):
        self.abi_name = abi_name
        self.so_name = so_name
        self.align = align # align >= 14 的就表示支持 16kb size