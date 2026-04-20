# -*- coding: utf-8 -*-
# Author: sens
# Date: 2025/8/21 13:10
import sys

from checker import run

# pip freeze > requirements.txt
# pip install -r requirements.txt
#
# pip install pyinstaller
# pyinstaller -F -n 16KbChecker main.py
#
# git tag v1.0.0
# git push origin v1.0.0
if __name__ == '__main__':
    run(sys.argv)
