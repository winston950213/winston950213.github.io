---
title: git报错：'fatal:remote origin already exists'
date: '2022-11-04T22:47:04+08:00'
permalink: 2022/11/04/git报错：-fatal-remote-origin-already-exists/
categories:
- 操作备忘
tags:
- bug
- git
comment: true
fancybox: true
---

只要两步，解决 `fatal:remote origin already exists`

<!-- more -->

1. 先删除
`$ git remote rm origin`
2. 重新添加
`git remote add origin git@github.com:username/repostery.git //关联本地仓库，远程库的名字为origin`
