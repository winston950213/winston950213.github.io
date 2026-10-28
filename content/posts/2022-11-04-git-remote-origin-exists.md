---
title: git报错：'fatal:remote origin already exists'
slug: git-remote-origin-exists
date: '2022-11-04T22:47:04+08:00'
category: 操作备忘
tags:
- bug
- git
summary: 两步处理 Git 远程仓库已存在时的 fatal 报错。
legacy_path: /2022/11/04/git报错：-fatal-remote-origin-already-exists/
legacy_url: https://coderdogz.github.io/2022/11/04/git%E6%8A%A5%E9%94%99%EF%BC%9A-fatal-remote-origin-already-exists/
featured: false
---

只要两步，解决 `fatal:remote origin already exists`

1. 先删除
`$ git remote rm origin`
2. 重新添加
`git remote add origin git@github.com:username/repostery.git //关联本地仓库，远程库的名字为origin`
