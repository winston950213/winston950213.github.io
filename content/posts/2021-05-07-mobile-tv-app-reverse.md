---
title: 移动TV
slug: mobile-tv-app-reverse
date: '2021-05-07T12:22:10+08:00'
category: 逆向学习
tags:
- 逆向
- 安卓
- Frida
- 抓包
summary: 移动 TV 客户端逆向分析过程。
legacy_path: /2021/05/07/移动TV/
legacy_url: https://coderdogz.github.io/2021/05/07/%E7%A7%BB%E5%8A%A8TV/
featured: false
---

实战移动TV,只分析了登录注册

> 更多详细内容可以参考指纹大佬的文章 ===> <https://bbs.pediy.com/thread-258776.htm>

## 抓包

指纹大佬文章说的抓不到包于是就上了 hook 抓包，hook 抓包是可以的，但是也可以使用 `postern + charles` , 在抓包这里没必要纠结太久 (-- 珍惜大佬), 使用 httpcanary 也行.
登录:
![文章插图](/blog/assets/images/legacy/20210507134616.png)
注册:
![文章插图](/blog/assets/images/legacy/20210507134713.png)

可以看到校验还是比较少的，需要分析参数也就 `memi1` , `key` , `rightkey` .

## 脱壳

脱壳工具现在有很多了，我这里使用的是 youpk, 使用方法很简单，只需要配置一下就可以，前提是有一台 pixel1

作者文章 ===> <https://bbs.pediy.com/thread-259854.htm>

## 参数分析

| 参数 | 值 | 处理 |
| --- | --- | --- |
| name | 1111111 | 传入 |
| pass | 123123 | 传入 |
| memi1 | afb9d9b6577c0397 | android id 写死 |
| key | 3820....dd72 | 包签名，写死 |
| rightkey | 376035775 | 包签名，写死 |
| register | register | register 字符串，login 同理 |

> apk 签名是不变的，android id 如果是要大批量生成，hook `android.os.Build` 应该可以，没测试

```shell
#内部类处理方法
android hooking search classes android.provider.Settings
android hooking watch class_method android.provider.Settings$Secure.getString --dump-args --dump-backtrace --dump-return
```
> 从哪里看出来，meli1 是 Android id?

这个 app 做了一定的混淆，把关键逻辑放到线程中去执行，这样打出来的调用栈就只有 Thread.run. 但是看到 onclick 方法: `v()` 返回的就是 `android id`

![文章插图](/blog/assets/images/legacy/20210507142705.png)

## 尾声

至于基于协议的登录注册，有手就行。我就不贴了

基本 objection 可以一把梭分析
