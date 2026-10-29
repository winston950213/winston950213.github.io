# Shoka 迁移与部署审计

审计对象：

- 官方文档：<https://fairy.vip/theme-shoka-doc/theme-shoka-doc/>
- 依赖说明：<https://fairy.vip/theme-shoka-doc/dependents/>
- 配置说明：<https://fairy.vip/theme-shoka-doc/config/>
- 特殊功能：<https://fairy.vip/theme-shoka-doc/special/>
- 当前站点：<https://winston950213.github.io/>
- 旧站：<https://coderdogz.github.io/>

## 官方要求对照

| 项目 | 当前状态 | 说明 |
| --- | --- | --- |
| Hexo 6.3.0 + Shoka 0.2.5 | 已满足 | 与旧站一致 |
| `hexo-renderer-multi-markdown-it` 0.1.5 | 已满足 | 代码块使用 Shoka 的 Prism 结构 |
| `hexo-autoprefixer` | 已满足 | CSS 自动补前缀 |
| `hexo-symbols-count-time` | 已满足 | 文章字数与阅读时长正常 |
| `hexo-feed` | 已满足 | RSS、Atom、JSON Feed 均生成 |
| `hexo-renderer-ejs` | 已补充 | 官方未列为依赖，但 Feed 的 EJS 模板需要它 |
| `highlight.enable: false` | 已满足 | 关闭默认高亮 |
| `prismjs.enable: false` | 已满足 | 由 multi-markdown-it 接管 |
| `markdown` 插件配置 | 已满足 | toc、multimd-table、furigana、spoiler |
| HTML/CSS 压缩 | 已满足 | `minify.html`、`minify.css` 开启 |
| JS 压缩 | 已关闭 | Shoka 自带压缩器会破坏生成后的 ES6 `app.js` |
| `autoprefixer.exclude` | 已满足 | 排除 `*.min.css` |
| 本地字体和图标 | 已满足 | 240 个字体文件与 iconfont 均在仓库内 |
| 搜索 | 未配置 | 没有 Algolia 凭据，搜索按钮已隐藏 |
| 评论 | 未启用 | 旧 LeanCloud 凭据返回 401，文章保持 `comment: false` |

## 本次发现并修复的问题

1. `source/js/fancybox.js` 被 Hexo 当成 Nunjucks 模板渲染，`{{poster}}`、`{{src}}` 被替换为空字符串，导致浏览器报语法错误。已用 `skip_render` 跳过。
2. `hexo-feed` 的 `rss.ejs`、`atom.ejs`、`json.ejs` 未编译，输出中直接出现 `<%= ... %>`。已安装 `hexo-renderer-ejs`，三种 Feed 均通过 XML/JSON 解析。
3. 社交图标 CSS 把 `github` 错写成 `.g`，颜色值还出现非法的 `thu`。已改为模板输出 `--social-color`，并在 exturl 转换时保留 `style`。
4. 未配置 Algolia 时搜索图标仍显示，点击无反应。已按 `config.algolia` 条件隐藏。
5. 404 页 canonical 指向不存在的 `/404`。已改为 `/404.html`。
6. GitHub Actions 的 `npm ci` 会因 `hexo-feed` 的 Hexo 4 peer dependency 失败。已改为 `npm ci --legacy-peer-deps --ignore-scripts`。

## 验证结果

- 20 篇文章全部生成，原文路由保持不变。
- 60 个站内页面在 1440px 下逐页测试，无 JS 异常、无横向溢出。
- 文章页 7 个代码块、69 个 Prism token、20 个目录链接正常。
- Fancybox 图片灯箱、主题明暗切换、代码复制、Pjax 导航正常。
- 390px 移动端首页、文章、归档、分类、标签页无横向溢出。
- 3825 个 HTML 内链/资源引用缺失 0 个。
- 721 个 CSS `url(...)` 引用缺失 0 个。
- `/rss.xml`、`/atom.xml` 各 20 条；`/feed.json` 20 条；`/sitemap.xml` 可解析。
- 线上 24 个关键页面复检：0 个 JavaScript 异常、0 个资源加载失败、0 个横向溢出。
- 线上 49 个 sitemap URL 全部返回 200；57 张正文/封面图片、240 个字体文件全部返回 200。
- 旧站深层文章地址会跳转到新站对应文章，例如 `/2021/05/23/抓包总结记录/`。

## 仍需外部条件的功能

- 站内搜索需要 Algolia 的 App ID、Search API Key 和索引；配置后可恢复搜索按钮。
- 评论需要可用的评论后端。旧站的 LeanCloud 应用凭据当前无法通过认证，因此没有把失效的评论框重新打开。
- 旧站是 GitHub Pages 上的 HTML/JavaScript 跳转并带 `noindex`，不是 HTTP 301；GitHub Pages 无法直接配置 301。
