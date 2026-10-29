---
title: 'Ubuntu安装curl报错：软件包有未满足的依赖关系： curl : 依赖: libcurl4 (= 7.58.0-2ubuntu3.10)'
date: '2022-11-04T22:39:03+08:00'
permalink: 2022/11/04/Ubuntu安装curl报错：软件包有未满足的依赖关系：-curl-依赖-libcurl4-7-58-0-2ubuntu3-10/
categories:
- 操作备忘
tags:
- bug
- ubuntu
comment: false
fancybox: true
---

依赖关系错误的老问题了

<!-- more -->

#### 错误重现

执行 `sudo apt install curl`
下列软件包有未满足的依赖关系：
curl : 依赖: libcurl4 (= 7.58.0-2ubuntu3.10) 但是 7.68.0-1ubuntu2.1 正要被安装
E: 无法修正错误，因为您要求某些软件包保持现状，就是它们破坏了软件包间的依赖关系。

#### 解决方法

依次执行:

1. `apt-get purge libcurl4`
2. `apt-get install curl`
