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
| 搜索 | Algolia | 已配置并索引 20 篇文章，搜索按钮已恢复 |
| 评论 | Giscus | 已接入 GitHub Discussions，20 篇文章已开启评论 |

## 本次发现并修复的问题

1. `source/js/fancybox.js` 被 Hexo 当成 Nunjucks 模板渲染，`{{poster}}`、`{{src}}` 被替换为空字符串，导致浏览器报语法错误。已用 `skip_render` 跳过。
2. `hexo-feed` 的 `rss.ejs`、`atom.ejs`、`json.ejs` 未编译，输出中直接出现 `<%= ... %>`。已安装 `hexo-renderer-ejs`，三种 Feed 均通过 XML/JSON 解析。
3. 社交图标 CSS 把 `github` 错写成 `.g`，颜色值还出现非法的 `thu`。已改为模板输出 `--social-color`，并在 exturl 转换时保留 `style`。
4. 未配置 Algolia 时搜索图标仍显示，点击无反应。已按 `config.algolia` 条件隐藏。
5. 404 页 canonical 指向不存在的 `/404`。已改为 `/404.html`。
6. GitHub Actions 的 `npm ci` 会因 `hexo-feed` 的 Hexo 4 peer dependency 失败。已改为 `npm ci --legacy-peer-deps --ignore-scripts`。
7. `source/_data/colors.styl` 覆盖了主题配色，但漏掉 `--nav-bg`，滚动后顶部导航背景会变透明。已补回渐变背景。
8. `source/_data/iconfont.styl` 漏掉 `.i-cloud` 和 `.i-bilibili` 图标定义，已从主题默认值补回。
9. 旧 Valine 后端已失效，评论改为 Giscus；主题不再加载 MiniValine。
10. Algolia 返回的 `path` 带前导斜杠，主题拼成 `//2021/...` 的错误链接；已改为正确的站内绝对路径。

## 验证结果

- 20 篇文章全部生成，原文路由保持不变。
- 60 个站内页面在 1440px 下逐页测试，无 JS 异常、无横向溢出。
- 抽查《抓包总结记录》：7 个代码块、69 个 Prism token、20 个目录链接正常。
- Fancybox 图片灯箱、主题明暗切换、代码复制、Pjax 导航正常。
- 390px 移动端首页、文章、归档、分类、标签页无横向溢出。
- 3825 个 HTML 内链/资源引用缺失 0 个。
- 721 个 CSS `url(...)` 引用缺失 0 个。
- `/rss.xml`、`/atom.xml` 各 20 条；`/feed.json` 20 条；`/sitemap.xml` 可解析。
- 线上 24 个关键页面复检：0 个 JavaScript 异常、0 个资源加载失败、0 个横向溢出。
- 线上 49 个 sitemap URL 全部返回 200；57 张正文/封面图片、240 个字体文件全部返回 200。
- 旧站深层文章地址会跳转到新站对应文章，例如 `/2021/05/23/抓包总结记录/`。
- 图片源复核：Gitee `coderdogz/blog_img` 中的 22 张原图与当前文件逐字节一致；其余 28 张的原始来源是 `cdn.jsdelivr.net/gh/coderdogz/img`，也与本地副本逐字节一致。20 篇文章的图片数量和顺序与旧站一致。
- 20 篇文章已接入 Giscus：评论 iframe 正常加载，明暗主题同步，Pjax 切换文章后讨论串会跟着更新。
- 评论页不再请求 MiniValine、`valine.min.js` 或 `comment.css`。
- Algolia 索引包含 20 篇文章；搜索“抓包”返回 4 条结果，结果链接均为正确的 `/2021/...` 站内路径。

## 仍需外部条件的功能

- 站内搜索使用 Algolia；`ALGOLIA_ADMIN_API_KEY` 保存在 GitHub Actions Secrets，构建时会重新索引 20 篇文章。
- Giscus 依赖 `giscus.app` 与 GitHub Discussions；如果访问 `giscus.app` 受阻，评论 iframe 可能无法加载。
- 旧站是 GitHub Pages 上的 HTML/JavaScript 跳转并带 `noindex`，不是 HTTP 301；GitHub Pages 无法直接配置 301。
