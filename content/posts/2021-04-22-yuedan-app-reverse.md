---
title: 约单
slug: yuedan-app-reverse
date: '2021-04-22T08:13:06+08:00'
category: 逆向学习
tags:
- 逆向
- 安卓
- Frida
- 实战
summary: 约单 App 的 Frida 与安卓逆向实战记录。
legacy_path: /2021/04/22/约单/
legacy_url: https://coderdogz.github.io/2021/04/22/%E7%BA%A6%E5%8D%95/
featured: false
---

约单app导游模块分析

## 抓包

> 这里使用 postern + charles 抓包

![文章插图](/blog/assets/images/legacy/20210422205012.png)

## 静态分析

> 通过抓包结果可知响应是加密的，请求参数也需要看一下。经过 jadx 静态反编译可以得知:

| 参数 | 分析结果 |
| --- | --- |
| GET | 请求方式 |
| `/api3.0/user/box` | `api{https://and.iyuedan.com/api3.0/user/box}` |
| `?tdid=388b6b40d00b627ce448595e2910f28d6` |  |
| `&time=1618816116054` | 时间戳 |
| `&oaid=null` | 写死 |
| `&token=1650097369I622d07d4e9IW66029678` | deviceId 写死 |
| `&role=1` | 写死 |
| `&version=6.1.6` | 写死 |
| `&sversion=1` | 写死 |
| `&client=android` | 写死 |
| `&device=Nexus 5X` | 写死 |
| `&appname=yuedan` | 写死 |
| `&market=xiaomi` | 写死 |
| `&os_version=27` | 写死 |
| `&new_work=27` | 写死 |
| `&lang=cn` | 写死 |
| `&ydmd=tmBmKE!VuK>H>E!_^K>H>` | 母鸡，写死 |
| `&and_class_name=Activity_UserInfo_V2` | 写死 |
| `&user_id=53745578` | 用户 id 写死 |
| `&position=2` | 写死 |
| `&ydtoken=6f9e3deb3afa8e2ccd4f015ca06fcef9` |  |
| `HTTP/1.1` | http 协议 |

经过分析，tdid 是不变化的，也有可能是登陆时候生成的 (没有分析), 接下来搜索 `ydtoken`

![文章插图](/blog/assets/images/legacy/20210423140255.png)

进过分析这里最为可疑，然后点进去看一下

![文章插图](/blog/assets/images/legacy/20210423140918.png)

可以看到这里是 MD5 加密，但是还是需要开启 objection 看一下.

![文章插图](/blog/assets/images/legacy/20210423141809.png)

但是在网页端使用 MD5 加密将原本的字符串加密之后结果并不一样，怀疑加盐了或者是自写的 MD5 加密，（但是一般不会是自写算法）. 我第一次在找盐的时候想错了。简单方法可以直接 hook 这个 md5 算法这样就会知道了

> 接着分析响应加密

具体怎么找到的我也忘记了，只记得先找到了这个 decrypt 函数

![文章插图](/blog/assets/images/legacy/20210423155651.png)

然后写 frida 脚本测试一下是可以调用成功的，但是在把算法抠出来写入却始终报错，然后再试了试 hook `convert` .

![文章插图](/blog/assets/images/legacy/20210423160545.png)

将这里的 `sohoKeyMap` 和 `devKeyMap` 重写，这样解密算法就完成了

至于如何做成接口调用这不是有手就行？

> 使用 springboot (不得不说 java 的代码是真的繁琐)

#### tips

1. 脱壳

   我使用的是 yang 神的脱壳工具 https://github.com/lasting-yang/frida_dump
2. 合并 dex

   合并 dex 的方法有多种方法，我使用的是

   > <https://github.com/Simp1er/AndroidSec/blob/master/dex2apk.py>

   

```python
import os
import zipfile
import argparse

def rename_class(path):
    files = os.listdir(path)
    dex_index = 0
    if path.endswith('/'):
        path = path[:-1]
        print(path)
    for i in range(len(files)):
        if files[i].endswith('.dex'):
            old_name = path + '/' + files[i]
            if dex_index == 0:
                new_name = path + '/' + 'classes.dex'
            else:
                new_name = path + '/' + 'classes%d.dex' % dex_index
            dex_index += 1
            if os.path.exists(new_name):
                continue
            os.rename(old_name, new_name)
    print('[*] 重命名完毕')

def extract_META_INF_from_apk(apk_path, target_path):
    r = zipfile.is_zipfile(apk_path)
    if r:
        fz = zipfile.ZipFile(apk_path, 'r')
        for file in fz.namelist():
            if file.startswith('META-INF'):
                fz.extract(file, target_path)
    else:
        print('[-] %s 不是一个APK文件' % apk_path)

def zip_dir(dirname, zipfilename):
    filelist = []
    if os.path.isfile(dirname):
        if dirname.endswith('.dex'):
            filelist.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            for dir in dirs:
                # if dir == 'META-INF':
                # print('dir:', os.path.join(root, dir))
                filelist.append(os.path.join(root, dir))
            for name in files:
                # print('file:', os.path.join(root, name))

                filelist.append(os.path.join(root, name))

    z = zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED)
    for tar in filelist:
        arcname = tar[len(dirname):]

        if ('META-INF' in arcname or arcname.endswith('.dex')) and '.DS_Store' not in arcname:
            # print(tar + " -->rar: " + arcname)
            z.write(tar, arcname)
    print('[*] APK打包成功，你可以拖入APK进行分析啦！'  )
    z.close()

def parse_args():
    parser = argparse.ArgumentParser(description='repackage dumped dex to apk for jeb/jadx analysis.')
    parser.add_argument('-a', '--apk_path', required=True, type=str,
                        help='apk for extracting META-INF')
    parser.add_argument('-i', '--dex_path', required=True, type=str,
                        help='path of dumped dex')
    parser.add_argument('-o', '--output', type=str, default="repacked.apk",
                        help='apk path after zip')
    args = parser.parse_args()
    #print(args.apk_path)
    return args

if __name__ == '__main__':
    args = parse_args()
    rename_class(args.dex_path)
    extract_META_INF_from_apk(args.apk_path, args.dex_path)
    # zip_file(args.dex_path)
    zip_dir(args.dex_path, args.output)
```

​ 但是有时候我们也许不要合并，使用 `ls -Sr` 将 dex 按照大小排列，1.2.0 版本的 jadx 可以使用 `add files` 将 dex 添加到项目中但是我添加了 6 个之后就崩了，但是不影响分析.
