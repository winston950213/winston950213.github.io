---
title: 再读[图解HTTP]
slug: http-illustrated-notes
date: '2021-05-19T07:27:53+08:00'
category: 读书笔记
tags:
- 网络
- 基础
summary: 《图解 HTTP》的阅读笔记与网络知识梳理。
legacy_path: /2021/05/19/再读-图解HTTP/
legacy_url: https://coderdogz.github.io/2021/05/19/%E5%86%8D%E8%AF%BB-%E5%9B%BE%E8%A7%A3HTTP/
featured: false
---

总的来说,这本书就好像是一本介绍http协议的发展史和一些基本的概念,基本没有很晦涩的概念

### 网络基础

#### TCP/IP 协议簇

- TCP/IP 协议簇 是互联网中所有协议的总称

![文章插图](/assets/images/legacy/20210521003401.png)

- TCP/IP 数据传输

![文章插图](/assets/images/legacy/20210521003445.png)

> TCP/IP 的模型是分为四层，OSI 网络模型是七层，不过有的人也分为五层

![文章插图](/assets/images/legacy/20210521004109.png)

- DNS 域名解析服务

  通过域名查找 IP 地址，或通过 IP 地址查找域名
- 三次握手与四次挥手

  ![文章插图](/assets/images/legacy/20210521010819.png)

> 在第三次握手的时候是可以传输数据的

![文章插图](/assets/images/legacy/20210521010903.png)

### HTTP 协议

- HTTP 协议无法保存状态
- HTTP 协议必须有客户端先发起请求
- HTTP 常用的请求方法
  - get, post, put, delete, options 等
- URL 和 URI
  - ...
- 由于 HTTP 是无状态且每进行一次 HTTP 通信就要断开一次 TCP 连接，所以为解决这些局限就产生了很多骚操作
  - 升级 HTTP 协议，建立一次 TCP 连接进行多次 HTTP 请求
  - 不等待响应，类似现在的异步
  - 使用 cookie 保存用户状态，避免多次请求

### HTTP 报文信息

> 这章感觉没什么实质的东西，主要就是编码，压缩和报文字段的解释

[http 报文头各字段详细含义](https://www.huaweicloud.com/articles/16e6fc0f95cd32a95dbf9ae5aa856193.html)

### HTTP 状态码

> 约定俗成的规矩，不遵守也没事.

![文章插图](/assets/images/legacy/20210521012126.png)

### HTTP 协议与 WEB 服务器

- 单台服务器托管多个域名

  脑子抽了，还去专门开了两个虚拟机去做实验，虚拟出来的服务器的内网 ip 地址是不同的，所以在内网访问的话，ip 地址不同所以不冲突。如果穿透到公网的话就会冲突，这样就需要将域名的 80 端口映射到 ip 地址不同的端口了.
- 数据转发

  - 代理 (此处指的是代理服务器)
    - 缓存代理服务器：将内容缓存到服务器上，如果请求的源内容未更新，则从缓存服务器返回
    - 透明代理服务器：对内容不做处理，反之则成为非透明服务器
    - 代理服务器可有多级，以 `Via` 首部进行区分
  - 网关
    - 网关可将 HTTP 协议转化为其他协议
    - 网关可以加密协议内容
    - 网关可以用各种方式去提高通信的安全性
  - 隧道
    - 进行加密通信内容
    - 将通信内容进行中转，一般用于远距离传输，防止信号衰弱
- 缓存

  - 客户端缓存
  - 缓存服务器缓存
  - 缓存有效时间

### HTTP 首部

> 都是一些常见的首部，不常见的用的也不多

### HTTPS

> `HTTPS` 就是 披着 SSL 外壳的 HTTP

- HTTPS 加密方式:

  - HTTPS 为了安全性使用混合加密方式对通信内容加密
    - 不使用对称加密是因为对称加密加解密的密钥相同，而且很容易倒推出原文
    - 使用混合加密方式，就是公开两把密钥，发送信息时使用对方公开的密钥进行加密，这样在对方接收到信息时就可以使用自己的密钥进行解密，避免了发送密钥时，密钥遭到窃取从而影响信息安全性
    - 公开两把密钥的缺点：无法确定公开的密钥一定是对方公开的且真实存在的密钥
  - 由于公开密钥的问题诞生了证书认证机构 CA
    - ![文章插图](/assets/images/legacy/20210522033046.png)
    - 证书机构的信誉很重要
- HTTPS 通信流程

  - ![文章插图](/assets/images/legacy/20210522033145.png)

### 通信中用户身份的认证

> 感觉现在大多是表单认证了，其他不是很多

- HTTP1.1 认证方式
- ![文章插图](/assets/images/legacy/20210522033419.png)

### 基于 HTTP 协议的追加协议

> 随着时代的发展，人们对网络传输的要求越来越高，于是诞生了许多解决 HTTP 协议痛点的追加协议

- Ajax 技术
- Comet 通信
- SPDY [为何会话层在表示层上面表示不理解]

  - ![文章插图](/assets/images/legacy/20210522033840.png)
  - 多路复用
  - 请求优先级
  - 压缩 HTTP 首部
  - 推送功能
  - 服务器提示功能
- WebScocket

  - ![文章插图](/assets/images/legacy/20210522035359.png)
- HTTP2.0

  - 作者写的时候还不成熟，但是现在已经在普及了
- 服务器管理文件的 WebDAV

### 构建 WEB 内容技术

- 静态 HTML
- 动态 HTML
- WEB 应用

  - CGI
  - Servlet
- 数据发布格式与语言

  - XML
  - HTML
  - JSON

### WEB 攻击技术

> 参考资料

1. <<图解 HTTP>>
2. [OSI 七层模型和 TCP/IP 四层模型以及五层模型](https://zhuanlan.zhihu.com/p/268196525)
3. [看懂 HTTPS、证书机构（CA）、证书、数字签名、私钥、公钥](https://yuhongjun.github.io/tech/2020/11/30/%E7%9C%8B%E6%87%82HTTPS-%E8%AF%81%E4%B9%A6%E6%9C%BA%E6%9E%84-CA-%E8%AF%81%E4%B9%A6-%E6%95%B0%E5%AD%97%E7%AD%BE%E5%90%8D-%E7%A7%81%E9%92%A5-%E5%85%AC%E9%92%A5.html)
4. [“三次握手，四次挥手” 你真的懂吗？](https://zhuanlan.zhihu.com/p/53374516)
