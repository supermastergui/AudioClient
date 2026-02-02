# AudioClient
一个语音客户端，使用Pyside6

## 如何使用
### 安装并配置环境
1. 安装PDM包管理器  
[请查看官方手册](https://pdm-project.org/zh-cn/latest/#_3)  
我们推荐使用`pipx`安装pdm  
安装好后请运行
```shell
pdm --version
```
输出类似`PDM, version x.xx.x`代表安装成功

2. 进入项目根目录, 运行下述命令
```shell
pdm install -G dev
```

3. 修改opuslib  
由于opuslib默认是查找系统是否安装了opus.dll  
如果您已经在电脑里安装了opus.dll  
则可以跳过这个步骤  
但如果您没有安装或者懒得安装  
请进入[`.venv/lib/site-packages/opuslib/api/__init__.py`](.venv/Lib/site-packages/opuslib/api/__init__.py)  
使用以下内容覆写该文件：
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
#

"""OpusLib Package."""

import ctypes  # type: ignore

from sys import platform
from ctypes.util import find_library  # type: ignore
from pathlib import Path

__author__ = 'Никита Кузнецов <self@svartalf.info>'
__copyright__ = 'Copyright (c) 2012, SvartalF'
__license__ = 'BSD 3-Clause License'

lib_location = find_library('opus')

root = Path.cwd() / "lib"

if lib_location is None:
    if platform == 'win32':
        lib_location = root / "opus.dll"
    elif platform == 'darwin':
        lib_location = root / "libopus.dylib"
    elif platform == 'linux':
        lib_location = root / "libopus.so"
    else:
        raise OSError("unupported platform")

    if not lib_location.exists():
        raise FileNotFoundError("libopus not found")

libopus = ctypes.CDLL(lib_location)

c_int_pointer = ctypes.POINTER(ctypes.c_int)
c_int16_pointer = ctypes.POINTER(ctypes.c_int16)
c_float_pointer = ctypes.POINTER(ctypes.c_float)
```

4. [可选]推荐安装pycharm的[mypy静态检查插件](https://plugins.jetbrains.com/plugin/25888-mypy)

5. 进入虚拟环境
```shell
# cmd
.\.venv\Scripts\activate.bat
# powershell
.\.venv\Scripts\activate
```

6. 生成资源文件
```shell
python generate_file.py
```

7. 运行主程序
```shell
python main.py
```

## 贡献者

<a href="https://github.com/FSD-Universe/AudioClient/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=FSD-Universe/AudioClient"  alt="作者头像"/>
</a>

## 开源协议

MIT License

Copyright © 2025-2026 Half_nothing

无附加条款。