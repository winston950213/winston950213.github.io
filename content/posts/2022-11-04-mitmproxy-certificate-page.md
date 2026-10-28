---
title: win10安装mitmproxy，成功之后访问mitm.it出现不了下载证书页面
slug: mitmproxy-certificate-page
date: '2022-11-04T22:41:09+08:00'
category: 操作备忘
tags:
- bug
- mitmproxy
- 代理
- 证书
summary: 排查 mitm.it 证书下载页无法打开的问题。
legacy_path: /2022/11/04/win10安装mitmproxy，成功之后访问mitm-it出现不了下载证书页面/
legacy_url: https://coderdogz.github.io/2022/11/04/win10%E5%AE%89%E8%A3%85mitmproxy%EF%BC%8C%E6%88%90%E5%8A%9F%E4%B9%8B%E5%90%8E%E8%AE%BF%E9%97%AEmitm-it%E5%87%BA%E7%8E%B0%E4%B8%8D%E4%BA%86%E4%B8%8B%E8%BD%BD%E8%AF%81%E4%B9%A6%E9%A1%B5%E9%9D%A2/
featured: false
---

浏览器代理老问题

### 错误重现

所有都安装好之后，各种检测都通过时候依旧出现不了证书下载页面。

此时检测一下浏览器或者计算机是否使用了代理【我就是因为使用了谷歌上网助手而导致不成功的 =-=】

### 解决方法

关闭所有代理工具，使用系统代理

### 插件推荐

使用 SwitchyOmega 是所有流量切换到固定端口，监听此端口

SwitchyOmega: 一个强大的代理切换工具 (官方自述)
