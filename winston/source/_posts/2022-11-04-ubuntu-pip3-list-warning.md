---
title: linux ubuntu pip3 list 出现警告
date: '2023-09-13 12:00:00'
permalink: 2022/11/04/linux-ubuntu-pip3-list-出现警告/
categories:
- 操作备忘
tags:
- bug
- ubuntu
comment: true
fancybox: true
---

#### 错误重现

<!-- more -->

```
 执行pip3 list后出现
```

`DEPRECATION: The default format will switch to columns in the future. You can use --format=(legacy|columns) (or define a format=(legacy|columns) in your pip.conf under the [list] section) to disable this warning.`

#### 解决方法

1. 在 `/etc` 下新建 `pip.conf` :
   `sudo nano /etc/pip.conf`
2. 写入
   `[list] format=columns`
   `ctrl x` Y 保存
3. 再次执行 `pip3 lsit`
