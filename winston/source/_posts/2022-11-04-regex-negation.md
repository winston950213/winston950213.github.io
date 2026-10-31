---
title: 正则表达式反选
date: '2022-08-05 12:00:00'
permalink: 2022/11/04/正则表达式反选/
categories:
- 操作备忘
tags:
- tips
- 正则
comment: true
fancybox: true
---

正则表达式骚操作之反选

<!-- more -->

## search 函数判断是否为 None

- 在有些时候我们使用 re 中的 search 的时候往往需要判断 search 里面的正则表达式是否为 None; 以前都是 `if ...else....` ; 这样当我们的正则表达式很长的时候写起来就和屎一样难看，虽然难看，但还是写了没办法～
- 现在使用 bool () 就可以直接把 search 结果转换为 true or flase 可以直接判断 ----->
  

```text
bool(re.search("hi", "abcdefghijkl"))
True

bool(re.search("hi", "abcdefgijkl"))
False
```

## 正则表达式反选

示例：

需要匹配出来 h1 标签 ps: 在实际开发中使用 h1 直接匹配太繁琐 so: 使用？！进行反选
`<(?!div).\*?text-align: center.\*?/(?!div).\*?>`
