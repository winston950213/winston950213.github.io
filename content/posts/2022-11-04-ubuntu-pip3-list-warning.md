---
title: linux ubuntu pip3 list 出现警告
slug: ubuntu-pip3-list-warning
date: '2022-11-04T22:37:05+08:00'
category: 操作备忘
tags:
- bug
- ubuntu
summary: 定位并清理 pip3 list 输出中的弃用警告。
legacy_path: /2022/11/04/linux-ubuntu-pip3-list-出现警告/
legacy_url: https://coderdogz.github.io/2022/11/04/linux-ubuntu-pip3-list-%E5%87%BA%E7%8E%B0%E8%AD%A6%E5%91%8A/
featured: false
---

#### 错误重现

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
