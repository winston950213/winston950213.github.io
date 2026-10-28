---
title: 'Ubuntu安装curl报错：软件包有未满足的依赖关系： curl : 依赖: libcurl4 (= 7.58.0-2ubuntu3.10)'
slug: ubuntu-curl-libcurl4
date: '2022-11-04T22:39:03+08:00'
category: 操作备忘
tags:
- bug
- ubuntu
summary: 处理 Ubuntu 安装 curl 时 libcurl4 版本依赖冲突。
legacy_path: /2022/11/04/Ubuntu安装curl报错：软件包有未满足的依赖关系：-curl-依赖-libcurl4-7-58-0-2ubuntu3-10/
legacy_url: https://coderdogz.github.io/2022/11/04/Ubuntu%E5%AE%89%E8%A3%85curl%E6%8A%A5%E9%94%99%EF%BC%9A%E8%BD%AF%E4%BB%B6%E5%8C%85%E6%9C%89%E6%9C%AA%E6%BB%A1%E8%B6%B3%E7%9A%84%E4%BE%9D%E8%B5%96%E5%85%B3%E7%B3%BB%EF%BC%9A-curl-%E4%BE%9D%E8%B5%96-libcurl4-7-58-0-2ubuntu3-10/
featured: false
---

依赖关系错误的老问题了

#### 错误重现

执行 `sudo apt install curl`
下列软件包有未满足的依赖关系：
curl : 依赖: libcurl4 (= 7.58.0-2ubuntu3.10) 但是 7.68.0-1ubuntu2.1 正要被安装
E: 无法修正错误，因为您要求某些软件包保持现状，就是它们破坏了软件包间的依赖关系。

#### 解决方法

依次执行:

1. `apt-get purge libcurl4`
2. `apt-get install curl`
