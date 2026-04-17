# -*- coding: utf-8 -*-
# Author: sens
# Date: 2025/8/21 13:10
import os
import sys

from checker import run


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(sys.argv[0])} <so_file | so_dir | apk_path | aab_path>")
        sys.exit(0)

    run(sys.argv[1])