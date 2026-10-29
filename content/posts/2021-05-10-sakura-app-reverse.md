---
title: 樱花
slug: sakura-app-reverse
date: '2021-05-10T17:12:53+08:00'
category: 逆向学习
tags:
- 逆向
- 安卓
- Frida
- 抓包
summary: 一次围绕樱花 App 的安卓逆向与抓包记录。
legacy_path: /2021/05/10/樱花/
legacy_url: https://coderdogz.github.io/2021/05/10/%E6%A8%B1%E8%8A%B1/
featured: false
---

实战樱花 app, 难度：有手就行，参数：请求 `req`

## 抓包

安装好之后先抓包，这次使用的是小黄鸟 + pixel

> 由于之前在 N5x 上面小黄鸟打开抓包之后 VPN 图标并不能正常出现，这次换了一个版本好了，就可以用了 (孕气好)

![文章插图](/assets/images/legacy/20210510172226.png)

通过抓包可以看到服务器地址为: `http://vip.yinlu.online/v1/svc/sms`

参数: `req=5rbFBgelHwvqcXtwsVAfWiMkqJ1cXwuEGEZmyEgOFjrmxVGEMK5jsTYpH1MHbo3yiPMCrO4J8OFeEw7HJyIH0qewUwcbSbH9fJ4N+Yz5ihb9cfCfFT8wnD+GOVy6x6ltWOVHjBNwwOqEzMTbDIFG0rD6CSwwwQBgteVJGiu7iRimwhkILBODqrqqgmmBTrKp0TxdgiLSwRbB6mXJhFItE1VXLhNlhZgbIz1L3DyN4gSmfPjXi79RkZTEqm8wE/wgZ0V4OVElEPWb7B6AA5MrVYWlbjse9Ht85SuLnUFYU1EqAPDq8/T52y6q5rtem1fP3n6Nq/HIU80z52ift5bibQdHDm/Vb3P0wm0hKnFk4UP5/dCZmUPbbSKKbQJQLslRL5vwjYEf7My2QDYysyeidd/ZlfsoF1K3ryB3jv/fg+3J+2XURyyB2eh9WbouB9T0kwYzvXts/jJmlH8HE5ZVCA==`

## 参数分析

使用 jadx 打开 apk, 可以看到只是混淆了并没有加壳，搜索 `v1/svc/sms` 可知:

![文章插图](/assets/images/legacy/20210510172742.png)

点进去可以看到下面有个 code get , 然后右键 `Find usage` , 只有两个结果看看就看到结果了

![文章插图](/assets/images/legacy/20210510173124.png)

使用 objection 快速验证 `e.h.a.f.h.e` 为收集参数值，在查看 `com.dasc.base_self_innovate.base_network.NetWorkStringUtil` 为调用加解密.

![文章插图](/assets/images/legacy/20210510174332.png)

![文章插图](/assets/images/legacy/20210510174419.png)

不继续分析了，其中有个 `sign` , 其实静态分析一下就行.
