---
title: win10安装mitmproxy，成功之后访问mitm.it出现不了下载证书页面
date: '2022-11-04T22:41:09+08:00'
permalink: 2022/11/04/win10安装mitmproxy，成功之后访问mitm-it出现不了下载证书页面/
categories:
- 操作备忘
tags:
- bug
- mitmproxy
- 代理
- 证书
comment: false
fancybox: true
---

浏览器代理老问题

<!-- more -->

### 错误重现

所有都安装好之后，各种检测都通过时候依旧出现不了证书下载页面。

此时检测一下浏览器或者计算机是否使用了代理【我就是因为使用了谷歌上网助手而导致不成功的 =-=】

### 解决方法

关闭所有代理工具，使用系统代理

### 插件推荐

使用 SwitchyOmega 是所有流量切换到固定端口，监听此端口

SwitchyOmega: 一个强大的代理切换工具 (官方自述)
