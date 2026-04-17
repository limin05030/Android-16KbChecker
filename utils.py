# -*- coding: utf-8 -*-
# Author: sens
# Date: 2026/4/16 13:43

import subprocess

def exec_cmd(cmd) -> (int, str):
    # print("exec:", cmd)
    # return subprocess.run(['ls'], capture_output=True, text=True).stdout
    _exitcode, _data = subprocess.getstatusoutput(cmd)
    return _exitcode, _data

