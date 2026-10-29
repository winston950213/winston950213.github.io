---
title: Command 'python setup.py egg_info' failed with error code 1 in /tmp/pip-build-thtq7d55/frida/
date: '2022-11-04T22:33:38+08:00'
permalink: 2022/11/04/Command-python-setup-py-egg-info-failed-with-error-code-1-in-tmp-pip-build-thtq7d55-frida/
categories:
- 操作备忘
tags:
- bug
- python
comment: false
fancybox: true
---

另一种方法解决 Command "python [setup.py](http://setup.py) egg_info" failed with error code 1 in /tmp/pip-build-thtq7d55/frida/

<!-- more -->

#### 错误重现

- ubuntu20.04 下安装执行 `pip3 install frida` 安装 frida 报错 `Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-build-thtq7d55/frida/`

#### 解决方法

- 搜索得知执行 `pip install --upgrade setuptools` 就可以
  ![文章插图](/images/legacy/202211042235236.png)
