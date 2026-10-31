# 折花酒肆

这是迁入 `winston950213` 账号后的文章仓库。当前线上站点使用旧站原版的 **Hexo 6.3.0 + Shoka 0.2.5** 主题构建。

- 线上地址：<https://winston950213.github.io/>
- 旧站：<https://coderdogz.github.io/>（已归档并跳转）
- 当前主题源码：[`winston/`](winston/)
- 现代主题备份标签：`modern-theme-20261029`

## 内容

- 48 篇迁移文章（博客园 41 篇去重后新增 28 篇，加站点原有 20 篇）
- 104 张正文本地图片（含 2 张 GIF 和 1 张失效原图占位）
- 99 张原站封面池
- 文章发布时间均匀分布在 2019-01 至 2025-06
- 分类、标签、归档、RSS、站点地图
- 原站 Shoka 的封面轮播、波浪、侧栏、文章目录、代码高亮、明暗模式和移动端布局

所有前端资源已随仓库提供，旧站的 Polyfill 和 jsDelivr 脚本已替换为本地版本，因此不会再卡在加载动画。

## 本地开发

```powershell
cd winston
npm ci --legacy-peer-deps --ignore-scripts
npx hexo clean
npx hexo generate
npx hexo server
```

本地预览地址通常为 <http://localhost:4000/>。

## 新增文章

在 `winston/source/_posts/` 新建 Markdown 文件：

```markdown
---
title: 文章标题
date: 2026-10-29 10:00:00
categories:
- 操作备忘
tags:
- Python
comment: true
---

正文从这里开始。
```

正文图片放在 `winston/source/images/legacy/` 或 `winston/source/images/cnblogs/`，通过对应站内路径引用。

## 博客园备份导入

```powershell
python legacy/import-cnblogs.py --dry-run
python legacy/import-cnblogs.py --write
```

导入计划与结果见 `legacy/cnblogs-import-plan.json` 和 `legacy/cnblogs-import-report.json`。脚本会保留 13 篇已存在的重复文章，只新增缺少的 28 篇，并把 48 篇文章的发布时间重新分配。

## 发布

推送到 `main` 后，GitHub Actions 会在 `winston/` 中运行 `hexo generate`，并发布 `winston/public/` 到 GitHub Pages。

评论使用 Giscus，配置在 `winston/_config.shoka.yml` 的 `giscus` 段，依赖仓库开启 Discussions 并安装 giscus app。站内搜索使用 Algolia，`ALGOLIA_ADMIN_API_KEY` 需要在 GitHub 仓库的 Actions Secrets 中维护。详细审计见 [`MIGRATION-AUDIT.md`](MIGRATION-AUDIT.md)。

## 目录

```text
winston/source/_posts/        文章 Markdown
winston/source/images/        文章图片、头像、原站封面
winston/source/_data/         原站封面图列表
winston/themes/shoka/         Shoka 0.2.5 主题及本地化依赖
legacy/                     旧站迁移快照与审计记录
```
