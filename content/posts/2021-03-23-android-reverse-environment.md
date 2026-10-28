---
title: 逆向环境搭建
slug: android-reverse-environment
date: '2021-03-23T15:55:29+08:00'
category: 逆向学习
tags:
- 逆向
- 安卓
summary: 基于 Kali Linux 搭建安卓逆向环境的完整备忘。
legacy_path: /2021/03/23/逆向环境搭建/
legacy_url: https://coderdogz.github.io/2021/03/23/%E9%80%86%E5%90%91%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA/
featured: false
---

基于kali linux 2019 的逆向环境搭建

> 本文基于 kali 2021.1, 种子地址:<https://www.offensive-security.com/kali-linux-vm-vmware-virtualbox-image-download/>

## 基本配置

### 修改用户及密码

> kali 开机默认账号 `kali` , 密码 `kali` , 一般在 root 用户下工作 (切勿用于生产环境)

```shell
sudo passwd root
New password:toor
Retype new password:toor
```

### 同步时区

> 新版本可能会自动修改时区，如为自动修改则使用以下方法:

```shell
dpkg-reconfigure tzdata
```

然后选择 `Asia→Shanghai`

### 安装中文字体

> 有些网页中文显示为乱码，许安装中文字体。新版本可能已经安装，如未自动安装则使用以下方法:

```shell
apt install xfonts-intl-chinese
apt install ttf-wqy-microhei
```

### 安装中文输入法

> 一般不建议安装
>
> <https://blog.csdn.net/qq_42333641/article/details/89325576>

```shell
apt-get update
apt-get install ibus ibus-pinyin
```
> 配置如文中图

![文章插图](/blog/assets/images/legacy/20210316011939.png)

### 修改电源设置

> 更改电源设置，防止息屏

![文章插图](/blog/assets/images/legacy/20210316013039.png)

![文章插图](/blog/assets/images/legacy/20210316013253.png)

### 切换到 bash

> kali 2021.1 默认使用 zsh, 在某些时候会出现问题，所以切换到 bash

`zsh` 切换到 `bash`

```shell
chsh -s /bin/bash
```

`bash` 切换到 `zsh`

```shell
chsh -s /bin/zsh
```
> 为防止重启终端不彻底直接 `reboot` 或者重启虚拟机使其生效

> 检查当前使用的 shell

```shell
echo $SHELL
echo $0
```

两个任选其一

### 增大历史缓存

> 有时候 app 数据太多，防止丢失

```shell
nano ~/.bashrc
```

![文章插图](/blog/assets/images/legacy/20210316014401.png)

在其后面增加三个 0, `Ctrl` + `x` + `Y` + `Enter` 保存退出.

`source ~/.bashrc` , 如果出现乱码，不要慌， `reooot`

## 工具安装

### htop , jnettop, tree

更新源

`apt update`

安装

`apt install htop jnettop tree`

### 安装 Android Studio

> 建议在真机复制链接到虚拟机使用 `wget`  下载

#### 下载

`wget //redirector.gvt1.com/edgedl/android/studio/ide-zips/4.1.2.0/android-studio-ide-201.7042882-linux.tar.gz`

#### 解压

使用 `tar zxvf FileName.tar.gz` 解压

#### 配置 adb

> 如果默认安装 Android Studio 的话，adb 位置为 `PATH=/root/Android/Sdk/platform-tools`

1. 执行在 `nano ~/.bashrc` 在 bashrc 中增加 `export PATH=/root/Android/Sdk/platform-tools:$PATH`
2. source 刷新
3. 输入 adb 不出现 `command not found` 则成功

#### 启动

1. 进入 /root/android-studio/bin
2. `./studio.sh`

#### 初始化第一个 Android 项目

> empty app 相信大家都会
>
> 静静等待初始化完成

问题:

> 在初始化 NDK 环境的时候会出现一个玄学问题

![文章插图](/blog/assets/images/legacy/20210316041950.jpg)

介绍几种解决方法:

- 大佬们的:

  1. 重新下载 SDK:

     由于没有领会到意思，我重新解压也未解决
  2. 删除原来下载的 NDK 文件夹，开代理重新下载

     > 开代理下载的 NDK 和不开代理下载的 NDK 不同，此法为解决版本冲突

     我试验了此法，未解决
  3. 手动下载 NDK

     > 在<https://developer.android.google.cn/ndk/downloads?hl=zh_cn> 下载 NDK, 手动配置

     未实验
- 我瞎猫碰着死耗子的做法

  > 瞎几把搜索，找到<https://developer.android.com/studio/projects/install-ndk?hl=zh-cn>, 于是我试着看看自己的 Android Studio

  安装 **CMake**, 就成功了

  ![文章插图](/blog/assets/images/legacy/20210323233719.png)

> 由于 NDK 已经安装过，就不需要再安装，只安装 CMake, 此时也不需要特定版本 [毕竟不是专业开发者]

### 科学配置

#### 命令行科学

##### proxychains

- 配置

  `nano /etc/proxychains4.conf`

  - 注释掉 proxy-dns
  - 注释掉 socks4
  - 增加自己配置 (主机 ip + 科学端口)

  ![文章插图](/blog/assets/images/legacy/20210316021834.png)

![文章插图](/blog/assets/images/legacy/20210316021917.png)

> **打开主机 VPN `Allow LAN` 即 允许局域网连接**

- 验证是否成功

  `proxychains curl ip.sb`

> 输出不是自己 ip 即成功

#### redsocks

> kali linux 自带，其他系统可能需要编译安装
>
> 遗留问题：浏览器访问 google 有问题，但是其他正常

1. 修改配置文件
   ![文章插图](/blog/assets/images/legacy/20210316045229.png)

> 前面的 log 开关可改可不改
> local_ip 与 local_port 可改可不改

2. [修改 iptables.sh](http://xn--iptables-0n3mm27o.sh)

![文章插图](/blog/assets/images/legacy/20210316045602.png)

> 框中为你的主机地址

3. 启动

```shell
redsocks
# 使用`iptables.sh`进行流量转发
sh iptables.sh
```

4. 验证

   - `ss -lntp|more` 查看监听端口
   - `ps aux | grep 进程名` 查看进程是否启动
   - `curl ip.sb`
5. 其他操作系统参照

   > <https://blog.csdn.net/zdy0_2004/article/details/48474721>
   >
   > <https://www.cnblogs.com/shaohef/p/4477862.html>
   >
   > > 笔者未实验

### 安装 jadx

- 在 github-releases 直接下载最新版 [https://github.com/skylot/jadx/releases (过程可能需要科学)](https://github.com/skylot/jadx/releases(%E8%BF%87%E7%A8%8B%E5%8F%AF%E8%83%BD%E9%9C%80%E8%A6%81%E7%A7%91%E5%AD%A6))
- `proxychains wgethttps://github.com/skylot/jadx/releases/download/v1.2.0/jadx-1.2.0.zip`
- `7z x jadx-1.2.0.zip -ojadx1.2.0` 解压即可使用 [-o 指定解压后的文件夹名]

### 安装 pyenv

> 安装尽量参照官方 README, 一般不会出现问题
>
> 以下实验均在 kali linux bash 下运行
>
> 官方地址 ==> <https://github.com/pyenv/pyenv>

1. 下载
   

```shell
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
```
2. 写入环境变量
   

```shell
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
```
3. 初始化
   

```shell
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc'
```
4. 刷新
   

```shell
exec "$SHELL"
```
5. 安装编译依赖
   

```text
sudo apt-get update; sudo apt-get install --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

   > <https://github.com/pyenv/pyenv/wiki#suggested-build-environment>
6. 常用命令

   - pyenv --version # 查看版本
   - pyrnv versions # 查看已经安装的 Python 版本
   - pyenv local 3.8.0 # 局部切换到 3.8.0
   - pyenv global system # 全局切换到 system, 即系统版本
   - pyenv --help # 查看帮助

### 安装 Miniconda

- 下载安装脚本: proxychains wget <https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh>
- 给安装脚本可执行权限: chmod +x Miniconda3-latest-Linux-x86_64.sh
- 运行安装脚本: sh Miniconda3-latest-Linux-x86_64.sh
- 安装过程脚本会自动修改 /.bashrc 文件，在脚本运行完毕最好检查一下 /.bashrc 文件并 source ~/.bashrc 刷新一下
- 安装 python3.8.0 环境:proxychains conda create -n py380 python=3.8.0
- 切换到 python3.8.0: conda activate py380
- 安装 frida 12.8.0 全家桶:

  

```bash
proxychains pip install frida==12.8.0
proxychains pip install frida-tools==5.3.0
proxychains pip install objection==1.8.4
```
  - 初始化环境就在 python 3.8.0 下:
    - 将 conda activate py380 写入～/.bashrc
    - 或将 alias mfrida="conda activate py380" 写入～/.bashrc
    - 手动切换也不是不行🙃

> 环境隔离 Miniconda 和 pyenv 二选一 (建议选择 conda)

### 安装 010editer

#### 安装

- 官网下载 ==><https://www.sweetscape.com/010editor/>
- 傻瓜式安装

#### 破解

> 破解可耻，请支持正版
>
> **无限试用法**

root 用户下删除 `/root/.local/share/SweetScape/010 Editor` 和 `/root/.config/SweetScape`

```shell
rm -rf /root/.config/SweetScape
rm -rf /root/.local/share/SweetScape/010 Editor
```

又来三十天

> 分析文章 ==> <https://blog.csdn.net/k7arm/article/details/108914024>

### 安装 Vscode

- 官网下载 vscode `proxychains wget https://vscode.cdn.azure.cn/stable/e5a624b788d92b8d34d1392e4c4d9789406efe8f/code_1.51.1-1605051630_amd64.deb`
- dpkg -i "刚才下载的 vscode"

### 安装 jeb

> <https://bbs.pediy.com/thread-259895-1.htm>

> 破解可耻，请支持正版

#### 下载

​ <https://mega.nz/file/OEJwWa7J#amoAEa0GGnWpWXaPYvGBC3E5FjciGYRXZpYiUTFDE8I>
​ or
​ <https://mir.cr/09UHCATD>

#### 安装

​ 解压运行 `./jeb_linux.sh`

#### 运行

​ 输入密码 `ilbtcdnwiuypbzeo` --> `Accept` --> `manual` 激活 (用户名自己定义)---> 拷贝 `License Data` ---> 使用 **Python2** 执行 `jebKeygen.py` ---> 粘贴 `License Data` ---> 拷贝 key---> 粘贴到 jeb---> 完成

### 安装 scrcpy

> 在 kali 中使用无线投屏，结合 WiFiadb

`apt search scrcpy`

`apt install scrcpy`

1. 使用 adb connect 连接手机
2. scrcpy 启动

### 安装 tmux

> 遇事不决，翻译提示
>
> 第一次启动出现一个让你执行 `touch ~/.hushlogin` 的提示，执行就完了

#### 安装

`apt install tmux`

#### 运行

`tmux`

> tmux 默认 `Ctrl` + `B` 为命令前缀

更多操作命令

> 可以参考阮一峰大佬的文章 ==><https://www.ruanyifeng.com/blog/2019/10/tmux.html>

## 踩坑及备忘

### VM

- vm 版本不要选择 15.0, 不要问为什么，问就是有坑，~~16.0 没有试过~~ 16 目前没发现什么大问题，目前选择 15.5 也是可以的
- vm 虚拟网络问题

  ![文章插图](/blog/assets/images/legacy/20210316141907.png)
  ![文章插图](/blog/assets/images/legacy/20210316141934.png)
  ![文章插图](/blog/assets/images/legacy/20210316142000.png)
- 如果出现了实在无法解决的问题，且此时你不想重新解压一份虚拟机文件可以试试

  ![文章插图](/blog/assets/images/legacy/20210316142015.png)
- 如果还有无法解决的问题，重新解压虚拟机，重新配置🙃
