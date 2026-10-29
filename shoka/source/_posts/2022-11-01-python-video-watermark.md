---
title: python为视频添加水印
date: '2022-11-01T00:50:08+08:00'
permalink: 2022/11/01/python为视频添加水印/
categories:
- 操作备忘
tags:
- python
- 水印
comment: false
fancybox: true
---

python 去水印

<!-- more -->

### 环境配置

**笔者环境：win10 专业版， python3.8.0**

- 官方文档：[https://zulko.github.io/moviepy/install.html【可能需要魔法】](https://zulko.github.io/moviepy/install.html%E3%80%90%E5%8F%AF%E8%83%BD%E9%9C%80%E8%A6%81%E9%AD%94%E6%B3%95%E3%80%91)

1. `pip install ez_setup`
2. `pip install moviepy`

#### 添加图片水印

```text

import moviepy.editor as mp

#本地视频位置
video = mp.VideoFileClip(r"D:\resource\myresource\4393644710024974337.mp4")

#准备log图片
logo = (mp.ImageClip(r"C:\Users\zrail\Downloads\touxiang.jpeg")
        .set_duration(video.duration) # 水印持续时间
        .resize(height=100) # 水印的高度，会等比缩放
        .margin(right=8, top=8, opacity=1) # 水印边距和透明度
        .set_pos(("left","center"))) # 水印的位置

final = mp.CompositeVideoClip([video, logo])
# mp4文件默认用libx264编码， 比特率单位bps
final.write_videofile("test.mp4", codec="libx264", bitrate="10000000")
```

##### 报错

1. `RuntimeError: The current Numpy installation ('C:\\Users\\zrail\\.conda\\envs\\py380\\lib\\site-packages\\numpy\\__init__.py') fails to pass a sanity check due to a bug in the windows runtime. See this issue for more information: https://tinyurl.com/y3dm3h86`

- 使用搜索引擎找到解决方案，切换 numpy 版本，链接：<https://github.com/numpy/numpy/issues/17726>

#### 添加文字水印

```text
# -*- coding: utf-8 -*-
from moviepy.editor import VideoFileClip,CompositeVideoClip

#本地视频位置
from moviepy.video.VideoClip import TextClip
#subclip视频截取开始时间和结束时间
video = VideoFileClip(r"D:\resource\myresource\4393644710024974337.mp4").subclip(0,1)

#制作文字，指定文字大小和颜色
txt_clip = ( TextClip("zxl shuiyin",fontsize=30,color='red')
             .set_position('center')#水印内容居中
             .set_duration(1) )#水印持续时间

result = CompositeVideoClip([video, txt_clip]) #在视频上覆盖文本
result.write_videofile("tttttest.mp4",fps=25)#fps:视频文件中每秒的帧数
```

##### 报错

1. `OSError: MoviePy Error: creation of None failed because of the following error:

[WinError 2] 系统找不到指定的文件。.

.This error can be due to the fact that ImageMagick is not installed on your computer, or (for Windows users) that you didn't specify the path to the ImageMagick binary in file [conf.py](http://conf.py), or that the path you specified is incorrect`

- 翻译报错信息并使用搜索引擎找到解决方案，链接：<https://stackoverflow.com/questions/51928807/moviepy-cant-detect-imagemagick-binary-on-windows>
- 安装 ImageMagick，并修改源码链接：<https://blog.csdn.net/qq_23944915/article/details/86514301>

> *具体没有仔细研究，水印的各种细节有待处理，这里只是抛砖引玉。剩下的靠大家了*
