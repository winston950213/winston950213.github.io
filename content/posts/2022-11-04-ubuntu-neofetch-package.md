---
title: 'E: Unable to locate package neofetch'
slug: ubuntu-neofetch-package
date: '2022-11-04T22:15:26+08:00'
category: 操作备忘
tags:
- bug
- ubuntu
summary: 为 Ubuntu 16.04 补齐软件源后安装 neofetch。
legacy_path: /2022/11/04/E-Unable-to-locate-package-neofetch/
legacy_url: https://coderdogz.github.io/2022/11/04/E-Unable-to-locate-package-neofetch/
featured: false
---

ubuntu16.04 在安装 `neofetch` 的时候会遇到 `E: Unable to locate package neofetch` , 这里提供一种解决方式

- 在遇到错误搜索之后发现，几乎所有的文章都是先 `sudo apt-get update` 然后 `sudo apt-get install neofetch` . 但是我都未解决我的问题
- 继续搜索之后发现这样可以解决
  1. `sudo add-apt-repository ppa:dawidd0811/neofetch`
  2. `sudo apt-get update`
  3. `sudo apt-get install neofetch`

> 来自一篇 16 年的文章:
> 原文指路 ==> <https://my.oschina.net/liuyuantao/blog/800375>
