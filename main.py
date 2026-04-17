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
if __name__ == '__main__':
    run(sys.argv)
