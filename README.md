# 折花酒肆

这是迁入 `winston950213` 账号后的文章仓库。当前线上站点使用旧站原版的 **Hexo 6.3.0 + Shoka 0.2.5** 主题构建。

- 线上地址：<https://winston950213.github.io/>
- 旧站：<https://coderdogz.github.io/>（已归档并跳转）
- 当前主题源码：[`shoka/`](shoka/)
- 现代主题备份标签：`modern-theme-20261029`

## 内容

- 20 篇迁移文章
- 50 张正文本地图片
- 6 张原站封面照片
- 分类、标签、归档、RSS、站点地图
- 原站 Shoka 的封面轮播、波浪、侧栏、文章目录、代码高亮、明暗模式和移动端布局

所有前端资源已随仓库提供，旧站的 Polyfill 和 jsDelivr 脚本已替换为本地版本，因此不会再卡在加载动画。

## 本地开发

```powershell
cd shoka
npm ci --legacy-peer-deps --ignore-scripts
npx hexo clean
npx hexo generate
npx hexo server
```

本地预览地址通常为 <http://localhost:4000/>。

## 新增文章

在 `shoka/source/_posts/` 新建 Markdown 文件：

```markdown
---
title: 文章标题
date: 2026-10-29 10:00:00
categories:
- 操作备忘
tags:
- Python
comment: false
---

正文从这里开始。
```

正文图片放在 `shoka/source/images/legacy/`，通过 `/images/legacy/文件名` 引用。

## 发布

推送到 `main` 后，GitHub Actions 会在 `shoka/` 中运行 `hexo generate`，并发布 `shoka/public/` 到 GitHub Pages。

站内搜索需要配置 `algolia`，评论需要可用的 Valine 后端；未配置时搜索图标会隐藏，文章默认不显示评论框。详细审计见 [`MIGRATION-AUDIT.md`](MIGRATION-AUDIT.md)。

## 目录

```text
shoka/source/_posts/        文章 Markdown
shoka/source/images/        文章图片、头像、原站封面
shoka/source/_data/         原站封面图列表
shoka/themes/shoka/         Shoka 0.2.5 主题及本地化依赖
legacy/                     旧站迁移快照与审计记录
```
