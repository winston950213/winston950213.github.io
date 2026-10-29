---
title: 抓包总结记录
date: '2021-05-23T20:50:13+08:00'
permalink: 2021/05/23/抓包总结记录/
categories:
- 逆向学习
tags:
- 逆向
- 安卓
- Frida
- 抓包
comment: false
fancybox: true
---

逆向学习中抓包的一点总结记录

<!-- more -->

## 计算机网络基础

> 互联网所有的数据都是基于网络传输，所以懂点网络在逆向过程中也是必不可少的

- http 与 https:

  - https 是披着 ssl 外壳的 http
  - <http://www.52im.net/thread-2866-1-1.html>
- 数据流向:

  > TCP/IP 协议中，数据流向都是按着这个模式来，无出其右

  ![文章插图](/images/legacy/20210521003445.png)

> OSI 网络模型 和 TCP/IP 模型的对比

![文章插图](/images/legacy/20210521004109.png)

> 读完 图解 HTTP 的一点碎碎念

- IP 协议与 IP 地址:
  - 我们经常说的 ip 一般表示 IP 地址，但是再谈到协议的时候 IP 一般指的是 IP 协议，并不是 IP 地址
- 代理 IP 与代理服务器
  - 代理 IP 分为透明代理，高匿等
    1. 透明代理：目标服务器知道你使用了代理，[原理为首部的 `via` , 说法来源于网上]
    2. 高匿代理：目标服务器不知道你使用了代理。这样会认为此次访问是一个真实的 IP 地址
  - 代理服务器分为透明代理服务器，缓存服务器
    1. 透明代理服务器：不对请求响应内容处理的服务器，只做代理。对请求响应内容更改的的称作非透明代理服务器
    2. 缓存代理服务器：将响应内容缓存到服务器，如果源服务器未更新资源则返回缓存内容
- 未完待续

## 基于工具的抓包

### charles + 系统代理

> 很早期的做法，但是随着 android7 以上不信任系统证书和检测手段增多现在不推荐这种抓包方式
>
> 从 OSI 模型理解，修改系统代理的抓包方式，代理存在于应用层，而使用 VPN 转发的方式抓包在网络层。代理的位置更加底层，更难防护

### charles + VPN 代理工具

> VPN 代理工具有很多，比如 Brook, postern, proxyDaivd, drony
>
> 笔者使用的是 postern, 觉得不怎么好，但是其他的用的也不怎么样好，相对之下选了一个相对好的就一直用了

#### 抓包环境搭建

1. charles 安装与配置 [破解可耻，支持正版]

   1. 官网下载最新版:<https://www.charlesproxy.com/assets/release/4.6.1/charles-proxy-4.6.1_amd64.tar.gz> 解压即可使用
   2. 破解 (行为可耻，请勿模仿):
      - 在 https://www.charles.ren/ 填写 Registered Name, 并生成授权码
      - ![文章插图](/images/legacy/20210524001004.png)
      - ![文章插图](/images/legacy/20210524001051.png)
2. postern 安装与配置

   1. 谷歌下载 postern
   2. ![文章插图](/images/legacy/20210524001259.png)
   3. ![文章插图](/images/legacy/20210524001344.png)
   4. ![文章插图](/images/legacy/20210524001413.png)
3. 证书安装

   1. charles 将证书导出到 PC, 导出为 pem 格式
   2. 计算文件名，文件名是一个 Hash 值，而后缀是一个数字。后缀名的数字是为了防止文件名冲突的，比如如果两个证书算出的 Hash 值是一样的话，那么一个证书的后缀名数字可以设置成 0，而另一个证书的后缀名数字可以设置成 1

```text
openssl x509 -subject_hash_old -in <Certificate_File>
```
   3. 修改证书名称
   4. 复制证书到设备上

      > 复制到系统目录并修改权限（安卓 8.1.0 Magisk Root）

      

```text
adb push xxxxxxx.0 /sdcard/
```

      

```bash
mount -o rw,remount /system 【不修改 没法写入】
mount -o rw,remount /
mv /sdcard/xxxxxxx.0 /etc/security/cacerts/ 移动文件到系统
chown root:root /etc/security/cacerts/xxxxxx.0 修改用户组
chmod 644 /system/etc/security/cacerts/xxxxxxx.0 修改权限
```
   5. 重启手机验证

      `reboot`

      —by:r0syue
   > 由于证书先安装到用户目录再移动到系统目录这样的操作会被 app 将此证书拉黑，如果曾经有过此操作最好先刷机在移动证书.

> 

```text
openssl x509 -subject_hash_old -in  <Certificate_File>报错 ：PEM routines:get_name:no start line:crypto\pem\pem_lib.c:745:Expecting: TRUSTED CERTIFICATE
```

> 解决办法：使用这个命令 `openssl x509 -subject_hash_old -in <Certificate_File> -inform der` by: 嘴强王者
> 系统证书目录： `/system/etc/security/cacerts/`

### HttpCany/Packet Capture

> 基于安卓手机。优点的话那就是省事。缺点的话可能是屏幕小

### Wireshark

> <https://book.douban.com/subject/21691692/>

### tcpdump

> <https://juejin.cn/post/6844904084168769549>

### 对抗

#### 证书

##### 证书锁定

> 在代码中指定证书 hash 值

##### 反证书锁定

1. 服务端校验客户端证书

   1. 使用 objection 自带命令

      `android sslpinning disable`

      ![文章插图](/images/legacy/20210521144416.png)
   2. 使用瘦蛟舞大佬的 DroidSSLUnpinning
      <https://github.com/WooyunDota/DroidSSLUnpinning>
   3. 使用 `JustTrustMe` , 当然了珍惜大佬的升级版本也可以

      - 原版: <https://github.com/Fuzion24/JustTrustMe>
      - 升级版: <https://github.com/w296488320/XposedOkHttpCat/tree/master/justTrustMePlush>
      - 分析文章: <https://bbs.pediy.com/thread-254114.htm>
   4. 自己分析 hook 点，去过掉证书锁定

      1. java.io.File
      2. java.security.KeyStore
      3. ...
2. 客户端校验服务端

   未完待续...
3. 双向验证

   > 典型的双向验证 Soul 分析，===> [soul 双向证书破解](http://zhaoxincheng.com/index.php/2020/07/15/oulapp%E7%9A%84%E5%8F%8C%E5%90%91%E8%AF%81%E4%B9%A6%E7%A0%B4%E8%A7%A3/)

   未完待续...

#### 检测系统代理

```text
System.getProperty(“http.proxyHost”);
System.getProperty(“http.proxyPort”);
```

#### 反系统代理检测

> 不使用系统代理的方式抓包，使用 VPN 代理方式

##### 检测 VPN

```bash
java.net.NetworkInterface.getName()
android.net.ConnectivityManager.getNetworkCapabilities()
```

##### 反 VPN 检测

> 分析 app,hook 掉检测

> 实战秀动 APP
>
> <https://mp.weixin.qq.com/s/UixExZkPWHJAT3jAD2sJJg>

---

- 看完这篇文章并跟着做了一遍，发现代码都一样，但是就是过不了，于是就使出了瞎几把 hook 大法，将 `ConnectivityManager` 类全部 hook, 然后修改 `getActiveNetwork` 返回值，最后成功

```javascript
Java.perform(
    function () {
        var ConnectivityManager = Java.use("android.net.ConnectivityManager");
        ConnectivityManager.getActiveNetwork.implementation = function () {
            var Integer = Java.use("android.net.Network")
            var r1 = Integer.$new(100)
            var result = this.getActiveNetwork();
            console.log("result is => ", result);
            return r1;
        }
    }
)
```

![文章插图](/images/legacy/20210523232011.jpg)

##### 文章收藏

<https://www.anquanke.com/post/id/197657>

<https://mp.weixin.qq.com/s/UixExZkPWHJAT3jAD2sJJg>

<https://www.jianshu.com/p/2476c8858daf>

<https://api-caller.com/2019/11/05/capture-note/>

### hook 抓包

> 这个仁者见仁智者见智，方法不尽相同，记录几个小工具，方便抄袭

- OkHttpLogger-Frida

  - [siyujie/OkHttpLogger-Frida: Frida 实现拦截 okhttp 的脚本](https://github.com/siyujie/OkHttpLogger-Frida)
- 基于 Okhttp 拦截器实现的各种抓包

  - <https://bbs.pediy.com/thread-252100.htm>
  - <https://bbs.pediy.com/thread-254503.htm>
  - 未完待续
- r0capture

  - [r0ysue/r0capture: 安卓应用层抓包通杀脚本](https://github.com/r0ysue/r0capture)

    > hook `ssl_read` , `ssl_write`
    >
    > 光看 hook 点可能觉得很简单，你上你也行，但是分析的过程很重要
- 自己分析，基于系统库的 hook

### 对抗

- anti_frida
- anti_xp

### 抓包骚操作

- Android 结合 Wireshark 抓包，不用安装证书

  - <https://github.com/lasting-yang/frida_bypass_ssl_example/tree/master/Android/android_wireshark_tls>
  - <https://www.52pojie.cn/thread-1405917-1-1.html>
- 高版本 android 证书问题

  - 将证书直接 push 到系统根目录下:

    - ![文章插图](/images/legacy/20210521165953.png)
    - <https://www.52pojie.cn/thread-1148892-1-1.html>
  - 编译 ROM

    - <https://www.52pojie.cn/thread-1382688-1-1.html>
