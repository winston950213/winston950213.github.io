# 折花酒肆

这是 `coderdogz` 的技术文章归档与新博客仓库。旧站自 2021 年开始使用 Hexo，后来因为主题依赖的外部脚本失效，首页长期停在加载动画。现在全部 20 篇文章已整理为 Markdown，并通过轻量静态生成器发布到 GitHub Pages。

线上地址：<https://coderdogz.github.io/blog/>

## 已完成的迁移

- 从旧站 JSON Feed 中提取全部 20 篇文章，并逐篇与旧站生成的页面核对。
- 保留原文正文、代码、分类、标签、发布时间和原始链接。
- 将 50 张正文配图收进 `public/assets/images/legacy/`，文章不再依赖 jsDelivr 或 Gitee 图片外链。
- 修复旧站中失效的加载脚本、`example.com` 站点地址和无法访问的资源。
- 生成文章详情、归档、分类、标签、全文搜索、RSS、站点地图和旧 URL 跳转页。
- 页面不依赖任何外部 JavaScript、字体或图片 CDN。

迁移审计结果在 [`legacy/migration-report.json`](legacy/migration-report.json)，原始 Feed 快照在 [`legacy/feed.json`](legacy/feed.json)。

## 本地预览

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/serve.py
```

打开 <http://127.0.0.1:4173/blog/>。

`scripts/serve.py` 会在本地模拟 GitHub Pages 的项目路径 `/blog`，方便直接验证绝对资源路径。

## 新增文章

在 `content/posts/` 新建 Markdown 文件：

```markdown
---
title: 文章标题
slug: article-slug
date: '2026-10-28T10:00:00+08:00'
category: 操作备忘
tags:
- Python
- 工具
summary: 用一两句话概括文章内容。
featured: false
---

正文从这里开始。
```

提交到 `main` 后，GitHub Actions 会自动构建并部署。文章中的本地图片放在 `public/assets/images/` 下，并通过 `/blog/assets/images/...` 引用。

## 目录结构

```text
content/
  pages/                 固定页面
  posts/                 Markdown 文章
legacy/                  旧站数据与迁移报告
public/assets/           图片等静态资源
scripts/build.py         静态站点生成器
scripts/import_legacy.py 旧站迁移脚本
src/static/              CSS 与浏览器端脚本
src/templates/           Jinja2 页面模板
```

## 发布方式

GitHub 仓库的 Pages Source 使用 **GitHub Actions**。工作流会先运行 `python scripts/build.py`，再将 `dist/` 作为 Pages artifact 发布。
