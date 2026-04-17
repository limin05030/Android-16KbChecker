# -*- coding: utf-8 -*-
# Author: sens
# Date: 2026/4/16 13:10

import os
import sys

from utils import exec_cmd

__app_default_config_name = "16KbChecker.config"

def __get_app_data_dir() -> str:
    # return os.path.join(os.getenv("APPDATA"), "16KbChecker")
    if sys.platform.startswith('win'):
        base = os.getenv('APPDATA')
        if not base:
            # 备用方案：使用用户目录下的 AppData
            base = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming')
    elif sys.platform.startswith('darwin'):  # macOS
        base = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    else:  # Linux 及其他类 Unix
        base = os.getenv('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))

    _data_dir = os.path.join(base, "16KbChecker")
    os.makedirs(_data_dir, exist_ok=True)  # 确保目录存在
    return _data_dir

def __search_android_sdk_in_environment() -> str | None:
    """通过环境变量或adb命令的路径找到sdk的路径"""

    adb_name = "adb.exe" if sys.platform.startswith("win") else "adb"

    # 检查环境变量 ANDROID_HOME
    _sdk_path = os.getenv("ANDROID_HOME")
    if _sdk_path:
        _adb_path = os.path.join(_sdk_path, "platform-tools", adb_name)
        if os.path.exists(_adb_path):
            return _sdk_path

    # 检查环境变量 ANDROID_SDK_ROOT
    _sdk_path = os.getenv("ANDROID_SDK_ROOT")
    if _sdk_path:
        _adb_path = os.path.join(_sdk_path, "platform-tools", adb_name)
        if os.path.exists(_adb_path):
            return _sdk_path

    # 检查 adb 命令路径
    if sys.platform.startswith("win"):
        _, _data = exec_cmd('where adb')
        if isinstance(_data, str) and _data.endswith('/adb.exe') and os.path.exists(_data):
            return os.path.dirname(os.path.dirname(_data))
    # elif sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
    else:
        _, _data = exec_cmd('which adb')
        if isinstance(_data, str) and _data.endswith('/adb') and os.path.exists(_data):
            return os.path.dirname(os.path.dirname(_data))

    return None

def __read_android_sdk_from_config() -> str | None:
    """从配置文件中读取sdk的路径"""

    _data_dir = __get_app_data_dir()
    if not os.path.exists(_data_dir):
        return None

    _config_file = os.path.join(_data_dir, __app_default_config_name)
    if not os.path.exists(_config_file):
        return None

    with open(_config_file, mode='r', encoding='utf-8') as f:
        adb_name = "adb.exe" if sys.platform.startswith("win") else "adb"
        for config_line in f.readlines():
            if '=' in config_line:
                k, v = config_line.replace('\n', '').split('=', maxsplit=1)
                k = k.strip()
                v = v.strip()
                if k == "sdk_dir" and len(v) > 0:
                    if os.path.exists(os.path.join(v, "platform-tools", adb_name)):
                        return v

    return None

def __find_android_sdk_path_window(path: str, max_deep: int) -> str | None:
    """在 Window 中递归搜索 Android SDK 路径"""
    if not isinstance(path, str) or len(path.strip()) == 0:
        return None

    if not os.path.isdir(path):
        return None

    if len(path.replace("\\", "/").split("/")) - 1 > max_deep:
        return None

    if os.path.exists(os.path.join(path, "platform-tools/adb.exe")):
        return path

    try:
        for f in os.listdir(path):
            if f in ["Windows", "Program Files", "Program Files (x86)", "ProgramData"]:
                continue

            _sdk_path = __find_android_sdk_path_window(os.path.join(path, f), max_deep)
            if _sdk_path:
                return _sdk_path
    except PermissionError:
        pass

    return None

def __find_android_sdk_path_unix(path: str, max_deep: int) -> str | None:
    """在 Unix/Linux/macOS 文件系统中递归搜索 Android SDK 路径"""
    if not isinstance(path, str) or len(path.strip()) == 0:
        return None

    if not os.path.isdir(path):
        return None

    # 计算当前路径深度（以 '/' 分隔）
    depth = path.rstrip('/').count('/') + 1 if path != '/' else 1
    if depth > max_deep:
        return None

    # 检查是否是 SDK 根目录（存在 platform-tools/adb）
    if os.path.exists(os.path.join(path, "platform-tools", "adb")):
        return path

    # 跳过常见的系统目录，避免无效扫描
    skip_dirs = {
        "bin", "boot", "dev", "etc", "lib", "lib64", "lost+found",
        "media", "mnt", "proc", "root", "run", "sbin", "srv", "sys",
        "tmp", "usr", "var",  # Linux 常见系统目录
        "System", "Library", "Applications", "Volumes", "Network",  # macOS 特有
        "home"  # 注意：跳过 /home 本身，但会递归进入 /home/username
    }

    try:
        for entry in os.listdir(path):
            # 跳过指定的系统目录
            if entry in skip_dirs:
                continue

            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                # 如果 entry 是 "home"，需要进入其子目录（用户目录）继续搜索
                if entry == "home":
                    try:
                        for user_dir in os.listdir(full_path):
                            user_full = os.path.join(full_path, user_dir)
                            if os.path.isdir(user_full):
                                result = __find_android_sdk_path_unix(user_full, max_deep)
                                if result:
                                    return result
                    except PermissionError:
                        continue
                else:
                    result = __find_android_sdk_path_unix(full_path, max_deep)
                    if result:
                        return result
    except PermissionError:
        pass

    return None

def __search_android_sdk_in_file_system() -> str | None:
    """在磁盘文件系统中搜索Android SDK的路径"""
    _sdk_path = None

    if sys.platform.startswith('win'):
        _drives = [chr(i) + ':' for i in range(ord('C'), ord('Z') + 1) if os.path.exists(chr(i) + ':')]
        for _drive in _drives:
            print(f"search android sdk in {_drive} ...")

            # 只搜索前两层目录
            _sdk_path = __find_android_sdk_path_window(f"{_drive}\\", max_deep=2)
            if _sdk_path:
                break
    elif sys.platform.startswith('darwin'):  # macOS
        print("search android sdk in / ...")
        _sdk_path = __find_android_sdk_path_unix("/", max_deep=8)
    else:  # Linux 及其他类 Unix
        print("search android sdk in / ...")
        _sdk_path = __find_android_sdk_path_unix("/", max_deep=8)

    # 搜索到了SDK，将SDK路径保存到配置文件中，以便下次使用时可以快速读取
    if _sdk_path:
        _data_dir = __get_app_data_dir()
        if not os.path.exists(_data_dir):
            os.makedirs(_data_dir)
        _config_file = os.path.join(_data_dir, __app_default_config_name)
        with open(_config_file, mode='w', encoding='utf-8') as f:
            f.write(f"sdk_dir={_sdk_path}\n")

    return _sdk_path

def get_android_sdk_path() -> str | None:
    """查找Android SDK的安装路径"""

    # 首先在环境变量中查找是否有adb命令
    _sdk_path = __search_android_sdk_in_environment()
    if _sdk_path:
        return _sdk_path

    # 尝试从配置记录中读取（上一次保存到配置文件中的）
    _sdk_path = __read_android_sdk_from_config()
    if _sdk_path:
        return _sdk_path

    # 遍历所有盘符查找sdk路径（找到后保存到配置文件中）
    print(f"search android sdk...")
    _sdk_path = __search_android_sdk_in_file_system()
    if _sdk_path:
        return _sdk_path

    print('android sdk path not found.')
    return None

def get_llvm_objdump_path() -> str | None:
    """获取llvm-objdump文件路径"""

    # android sdk path
    sdk_path = get_android_sdk_path()
    if not sdk_path:
        print("Android SDK path not found.")
        return None

    # NDK path
    ndk_path = os.path.join(sdk_path, "ndk")
    if not os.path.isdir(ndk_path):
        print("You haven't downloaded the ndk yet, please download it first.")
        return None

    ndk_versions = (os.listdir(ndk_path))
    if len(ndk_versions) == 0:
        print("You haven't downloaded the ndk yet, please download it first.")
        return None

    llvm_objdump = "llvm-objdump.exe" if sys.platform.startswith('win') else "llvm-objdump"
    ndk_versions.sort(reverse=True)
    for ndk_version in ndk_versions:
        temp_path = os.path.join(ndk_path, ndk_version, "toolchains", "llvm", "prebuilt")
        if not os.path.exists(temp_path):
            continue

        # prebuilt 的下一个目录各平台都不一样，需要动态获取
        # 一般情况下这里只会有一个子目录
        platform_abi_names = os.listdir(temp_path)
        if len(platform_abi_names) == 0:
            continue

        for platform_abi_name in platform_abi_names:
            objdump_path = os.path.join(temp_path, platform_abi_name, "bin", llvm_objdump)
            if os.path.exists(objdump_path):
                return objdump_path

    print(f"{llvm_objdump} not found, please upgrade your NDK version.")
    return None


if __name__ == '__main__':
    get_android_sdk_path()