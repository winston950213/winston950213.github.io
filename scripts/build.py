#!/usr/bin/env python3
"""Build the static article archive."""

from __future__ import annotations

import html
import hashlib
import json
import math
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote

import yaml
from bs4 import BeautifulSoup, NavigableString
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt
from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.util import ClassNotFound


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content"
POSTS_DIR = CONTENT_DIR / "posts"
PAGES_DIR = CONTENT_DIR / "pages"
TEMPLATES_DIR = ROOT / "src" / "templates"
STATIC_DIR = ROOT / "src" / "static"
PUBLIC_DIR = ROOT / "public"
DIST_DIR = ROOT / "dist"

TAG_SLUGS = {
    "逆向": "reverse-engineering",
    "安卓": "android",
    "抓包": "packet-capture",
    "证书": "certificate",
    "基础": "fundamentals",
    "网络": "network",
    "代理": "proxy",
    "备忘": "notes",
    "工具": "tools",
    "网址": "bookmarks",
    "多线程": "multithreading",
    "水印": "watermark",
    "正则": "regex",
    "实战": "practice",
    "Frida": "Frida",
}

CATEGORY_SLUGS = {
    "操作备忘": "operations",
    "编程语言": "programming",
    "读书笔记": "reading",
    "逆向学习": "reverse-engineering",
}

CATEGORY_DESCRIPTIONS = {
    "操作备忘": "系统配置、开发工具与踩坑记录",
    "编程语言": "Python 与代码实践",
    "读书笔记": "技术阅读与知识梳理",
    "逆向学习": "安卓、抓包、Frida 与逆向实战",
}

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
WORD_RE = re.compile(r"[A-Za-z0-9_]+")


@dataclass
class Post:
    meta: dict[str, Any]
    body: str
    source_path: Path
    html_content: str = ""
    toc: str = ""
    plain_text: str = ""
    reading_minutes: int = 1
    word_count: int = 0
    url: str = ""
    date_display: str = ""
    date_short: str = ""
    date_iso: str = ""
    category_slug: str = ""
    tags: list[dict[str, str]] = field(default_factory=list)

    @property
    def title(self) -> str:
        return str(self.meta["title"])

    @property
    def slug(self) -> str:
        return str(self.meta["slug"])

    @property
    def summary(self) -> str:
        return str(self.meta.get("summary", ""))

    @property
    def category(self) -> str:
        return str(self.meta.get("category", "技术笔记"))

    @property
    def date(self) -> datetime:
        value = self.meta["date"]
        return value if isinstance(value, datetime) else datetime.fromisoformat(str(value))


def safe_slug(value: str) -> str:
    if value in TAG_SLUGS:
        return TAG_SLUGS[value]
    ascii_slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return ascii_slug or quote(value, safe="")


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"Missing YAML frontmatter: {path}")
    metadata = yaml.safe_load(match.group(1)) or {}
    return metadata, match.group(2).strip() + "\n"


def count_reading(text: str) -> tuple[int, int]:
    cjk = len(CJK_RE.findall(text))
    words = len(WORD_RE.findall(text))
    total = cjk + words
    minutes = max(1, math.ceil(cjk / 330 + words / 210))
    return total, minutes


def linkify_plain_text(text: str) -> str:
    text = re.sub(r"https?://\S+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def heading_slug(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip().lower()
    value = re.sub(r"[^\w\u3400-\u4dbf\u4e00-\u9fff-]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "section"


def make_toc(headings: list[dict[str, Any]]) -> str:
    if not headings:
        return ""

    root: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    for heading in headings:
        node = {**heading, "children": []}
        while stack and stack[-1]["level"] >= node["level"]:
            stack.pop()
        if stack:
            stack[-1]["children"].append(node)
        else:
            root.append(node)
        stack.append(node)

    def render_nodes(nodes: list[dict[str, Any]]) -> str:
        parts = ["<ul>"]
        for node in nodes:
            parts.append(
                f'<li><a href="#{html.escape(node["id"], quote=True)}">'
                f'{html.escape(node["text"])}</a>'
            )
            if node["children"]:
                parts.append(render_nodes(node["children"]))
            parts.append("</li>")
        parts.append("</ul>")
        return "".join(parts)

    return f'<div class="toc">{render_nodes(root)}</div>'


def highlight_code(code: str, language: str) -> str:
    lexer = None
    if language:
        try:
            lexer = get_lexer_by_name(language)
        except ClassNotFound:
            lexer = None
    lexer = lexer or TextLexer()
    return pygments_highlight(code, lexer, HtmlFormatter(nowrap=True))


def render_fence(
    renderer: Any,
    tokens: list[Any],
    index: int,
    options: dict[str, Any],
    env: dict[str, Any],
) -> str:
    token = tokens[index]
    info = token.info.strip()
    language = info.split(maxsplit=1)[0] if info else ""
    code = token.content
    highlighted = highlight_code(code, language)
    class_name = f' class="language-{html.escape(language)}"' if language else ""
    return (
        '<div class="highlight"><pre>'
        f"<code{class_name}>{highlighted}</code>"
        "</pre></div>\n"
    )


def enhance_article_html(rendered: str) -> tuple[str, str]:
    soup = BeautifulSoup(rendered, "lxml")

    for image in soup.find_all("img"):
        image["loading"] = "lazy"
        image["decoding"] = "async"
        if not image.get("alt"):
            image["alt"] = "文章插图"

    for link in soup.find_all("a", href=True):
        href = str(link["href"])
        if href.startswith(("http://", "https://")):
            link["target"] = "_blank"
            link["rel"] = "noopener noreferrer"
            if href.startswith("http://"):
                link["data-insecure"] = "true"
        elif href.startswith("#"):
            link["href"] = "#" + unquote(href[1:])

    for item in soup.select("li"):
        text_node = next(
            (
                node
                for node in item.find_all(string=True)
                if str(node).strip()
                and not node.find_parent(["pre", "code", "script", "style"])
            ),
            None,
        )
        if text_node is None:
            continue
        original = str(text_node)
        task_match = re.match(r"^\s*\[([ xX])\]\s*", original)
        if task_match:
            checked = task_match.group(1).lower() == "x"
            replacement = soup.new_tag("input")
            replacement["type"] = "checkbox"
            replacement["disabled"] = "disabled"
            if checked:
                replacement["checked"] = "checked"
            item["class"] = item.get("class", []) + ["task-item"]
            text_node.replace_with(replacement)
            replacement.insert_after(NavigableString(original[task_match.end():]))

    for table in soup.find_all("table"):
        if table.parent and table.parent.name == "div" and "table-wrap" in table.parent.get("class", []):
            continue
        wrapper = soup.new_tag("div", **{"class": "table-wrap"})
        table.wrap(wrapper)

    return str(soup), linkify_plain_text(soup.get_text(" ", strip=True))


def render_markdown(body: str) -> tuple[str, str, str]:
    converter = MarkdownIt(
        "commonmark",
        {
            "html": True,
            "linkify": False,
            "typographer": False,
            "highlight": highlight_code,
        },
    )
    converter.enable("table").enable("strikethrough")
    converter.add_render_rule("fence", render_fence)
    rendered = converter.render(body)
    rendered, plain = enhance_article_html(rendered)

    soup = BeautifulSoup(rendered, "lxml")
    used_ids: Counter[str] = Counter()
    headings: list[dict[str, Any]] = []
    for heading in soup.find_all(re.compile(r"^h[2-4]$")):
        text = heading.get_text(" ", strip=True)
        base_id = heading.get("id") or heading_slug(text)
        used_ids[base_id] += 1
        heading_id = base_id if used_ids[base_id] == 1 else f"{base_id}-{used_ids[base_id]}"
        heading["id"] = heading_id
        headings.append(
            {
                "level": int(heading.name[1]),
                "id": heading_id,
                "text": text,
            }
        )
    return str(soup), make_toc(headings), plain


def load_posts(site: dict[str, Any]) -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        meta, body = parse_frontmatter(path)
        for required in ("title", "slug", "date", "category", "summary"):
            if not meta.get(required):
                raise ValueError(f"{path} is missing frontmatter field {required!r}")

        post = Post(meta=meta, body=body, source_path=path)
        rendered, toc, plain = render_markdown(body)
        post.html_content = rendered
        post.toc = toc
        post.plain_text = plain
        post.word_count, post.reading_minutes = count_reading(plain)
        post.url = f"{site['base_path']}/posts/{post.slug}/"
        post.date_display = post.date.strftime("%Y 年 %m 月 %d 日")
        post.date_short = post.date.strftime("%m.%d")
        post.date_iso = post.date.isoformat()
        post.category_slug = CATEGORY_SLUGS.get(post.category, safe_slug(post.category))
        post.tags = [
            {
                "name": str(tag),
                "slug": safe_slug(str(tag)),
                "url": f"{site['base_path']}/tags/{safe_slug(str(tag))}/",
            }
            for tag in meta.get("tags", [])
        ]
        posts.append(post)

    posts.sort(key=lambda item: item.date, reverse=True)
    return posts


def write_html(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def page_url(site: dict[str, Any], path: str) -> str:
    return f"{site['base_url']}{path}"


def build_tags(site: dict[str, Any], posts: list[Post]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for post in posts:
        counts.update(tag["name"] for tag in post.tags)
    tags = []
    for name, count in counts.items():
        slug = safe_slug(name)
        tags.append(
            {
                "name": name,
                "slug": slug,
                "count": count,
                "url": f"{site['base_path']}/tags/{slug}/",
            }
        )
    return sorted(tags, key=lambda item: (-item["count"], item["name"].lower()))


def build_categories(site: dict[str, Any], posts: list[Post]) -> list[dict[str, Any]]:
    counts = Counter(post.category for post in posts)
    categories = []
    for name, count in counts.items():
        slug = CATEGORY_SLUGS.get(name, safe_slug(name))
        categories.append(
            {
                "name": name,
                "slug": slug,
                "count": count,
                "description": CATEGORY_DESCRIPTIONS.get(name, "技术随笔与学习记录"),
                "url": f"{site['base_path']}/categories/{slug}/",
            }
        )
    return sorted(categories, key=lambda item: (-item["count"], item["name"]))


def build_rss(site: dict[str, Any], posts: list[Post]) -> str:
    updated = posts[0].date if posts else datetime.now()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{html.escape(site['title'])}</title>",
        f"    <link>{html.escape(site['base_url'] + site['base_path'] + '/')}</link>",
        f"    <description>{html.escape(site['description'])}</description>",
        f"    <language>{html.escape(site['language'])}</language>",
        f"    <lastBuildDate>{updated.strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>",
        f'    <atom:link href="{html.escape(site["base_url"] + site["base_path"] + "/feed.xml")}" rel="self" type="application/rss+xml"/>',
    ]
    for post in posts:
        lines.extend(
            [
                "    <item>",
                f"      <title>{html.escape(post.title)}</title>",
                f"      <link>{html.escape(page_url(site, post.url))}</link>",
                f"      <guid isPermaLink=\"true\">{html.escape(page_url(site, post.url))}</guid>",
                f"      <pubDate>{post.date.strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate>",
                f"      <description>{html.escape(post.summary)}</description>",
                "    </item>",
            ]
        )
    lines.extend(["  </channel>", "</rss>", ""])
    return "\n".join(lines)


def build_sitemap(site: dict[str, Any], paths: list[str]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path in paths:
        lines.append(f"  <url><loc>{html.escape(page_url(site, path))}</loc></url>")
    lines.extend(["</urlset>", ""])
    return "\n".join(lines)


def load_page(name: str) -> tuple[dict[str, Any], str]:
    return parse_frontmatter(PAGES_DIR / f"{name}.md")


def main() -> None:
    if DIST_DIR.parent != ROOT:
        raise RuntimeError(f"Refusing to clean unexpected output directory: {DIST_DIR}")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    site = yaml.safe_load((ROOT / "site.yaml").read_text(encoding="utf-8"))
    posts = load_posts(site)
    if not posts:
        raise RuntimeError("No posts found")

    tags = build_tags(site, posts)
    categories = build_categories(site, posts)
    years: dict[int, list[Post]] = defaultdict(list)
    for post in posts:
        years[post.date.year].append(post)

    tag_index = {tag["name"]: tag for tag in tags}
    category_index = {category["name"]: category for category in categories}
    for post in posts:
        post.meta["category_url"] = category_index[post.category]["url"]
        post.meta["category_slug"] = post.category_slug

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["shortdate"] = lambda value: value.strftime("%m.%d")

    common = {
        "site": site,
        "nav_tags": tags[:7],
        "nav_categories": categories,
        "current_year": datetime.now().year,
        "total_words": sum(post.word_count for post in posts),
        "total_posts": len(posts),
        "total_tags": len(tags),
        "total_categories": len(categories),
        "all_tags": tags,
        "all_categories": categories,
    }
    static_payload = b"".join(
        (STATIC_DIR / filename).read_bytes()
        for filename in ("site.css", "app.js")
    )
    common["asset_version"] = hashlib.sha1(static_payload).hexdigest()[:12]

    index_template = env.get_template("index.html")
    post_template = env.get_template("article.html")
    archive_template = env.get_template("archive.html")
    tag_template = env.get_template("tag.html")
    category_template = env.get_template("category.html")
    about_template = env.get_template("about.html")
    not_found_template = env.get_template("404.html")
    legacy_template = env.get_template("legacy-redirect.html")
    search_template = env.get_template("search.html")

    latest = posts[:6]
    featured = next((post for post in posts if post.meta.get("featured")), posts[0])
    recent = [post for post in posts if post is not featured][:5]

    write_html(
        DIST_DIR / "index.html",
        index_template.render(
            **common,
            page_title=None,
            page_description=site["description"],
            canonical_url=page_url(site, f"{site['base_path']}/"),
            latest=latest,
            featured=featured,
            recent=recent,
            years=years,
            body_class="home-page",
        ),
    )

    for index, post in enumerate(posts):
        older = posts[index + 1] if index + 1 < len(posts) else None
        newer = posts[index - 1] if index > 0 else None
        path = f"{site['base_path']}/posts/{post.slug}/"
        write_html(
            DIST_DIR / "posts" / post.slug / "index.html",
            post_template.render(
                **common,
                post=post,
                older=older,
                newer=newer,
                page_title=post.title,
                page_description=post.summary,
                canonical_url=page_url(site, path),
                body_class="post-page",
            ),
        )

        legacy_path = str(post.meta.get("legacy_path", "")).strip("/")
        if legacy_path:
            write_html(
                DIST_DIR / legacy_path / "index.html",
                legacy_template.render(
                    **common,
                    target_url=post.url,
                    canonical_url=page_url(site, post.url),
                    body_class="redirect-page",
                ),
            )

    archive_path = f"{site['base_path']}/archives/"
    write_html(
        DIST_DIR / "archives" / "index.html",
        archive_template.render(
            **common,
            years=dict(sorted(years.items(), reverse=True)),
            page_title="归档",
            page_description=f"{site['title']}的全部文章归档",
            canonical_url=page_url(site, archive_path),
            body_class="archive-page",
        ),
    )

    tag_index_path = f"{site['base_path']}/tags/"
    write_html(
        DIST_DIR / "tags" / "index.html",
        archive_template.render(
            **common,
            tags=tags,
            years={},
            page_title="标签",
            page_description="按标签浏览全部文章",
            canonical_url=page_url(site, tag_index_path),
            body_class="tags-page",
            tag_view=True,
        ),
    )

    category_index_path = f"{site['base_path']}/categories/"
    write_html(
        DIST_DIR / "categories" / "index.html",
        archive_template.render(
            **common,
            tags=[],
            categories=categories,
            years={},
            page_title="分类",
            page_description="按主题分类浏览全部文章",
            canonical_url=page_url(site, category_index_path),
            body_class="categories-page",
            category_view=True,
        ),
    )

    for tag in tags:
        tag_posts = [post for post in posts if any(item["name"] == tag["name"] for item in post.tags)]
        write_html(
            DIST_DIR / "tags" / tag["slug"] / "index.html",
            tag_template.render(
                **common,
                tag=tag,
                posts=tag_posts,
                page_title=f"标签：{tag['name']}",
                page_description=f"包含标签 {tag['name']} 的文章",
                canonical_url=page_url(site, tag["url"]),
                body_class="tag-page",
            ),
        )
        if tag["name"] != tag["slug"] and tag["name"].casefold() != tag["slug"].casefold():
            write_html(
                DIST_DIR / "tags" / tag["name"] / "index.html",
                legacy_template.render(
                    **common,
                    target_url=tag["url"],
                    canonical_url=page_url(site, tag["url"]),
                    body_class="redirect-page",
                ),
            )

    for category in categories:
        category_posts = [post for post in posts if post.category == category["name"]]
        write_html(
            DIST_DIR / "categories" / category["slug"] / "index.html",
            category_template.render(
                **common,
                category=category,
                posts=category_posts,
                page_title=f"分类：{category['name']}",
                page_description=category["description"],
                canonical_url=page_url(site, category["url"]),
                body_class="category-page",
            ),
        )
        write_html(
            DIST_DIR / "categories" / category["name"] / "index.html",
            legacy_template.render(
                **common,
                target_url=category["url"],
                canonical_url=page_url(site, category["url"]),
                body_class="redirect-page",
            ),
        )

    write_html(
        DIST_DIR / "page" / "2" / "index.html",
        legacy_template.render(
            **common,
            target_url=f"{site['base_path']}/archives/",
            canonical_url=page_url(site, f"{site['base_path']}/archives/"),
            body_class="redirect-page",
        ),
    )

    about_meta, about_body = load_page("about")
    about_rendered, _, _ = render_markdown(about_body)
    write_html(
        DIST_DIR / "about" / "index.html",
        about_template.render(
            **common,
            about_html=about_rendered,
            page_title="关于",
            page_description=about_meta.get("summary", site["description"]),
            canonical_url=page_url(site, f"{site['base_path']}/about/"),
            body_class="about-page",
        ),
    )

    write_html(
        DIST_DIR / "search" / "index.html",
        search_template.render(
            **common,
            page_title="搜索",
            page_description="搜索文章、标签与分类",
            canonical_url=page_url(site, f"{site['base_path']}/search/"),
            body_class="search-page",
        ),
    )

    write_html(
        DIST_DIR / "404.html",
        not_found_template.render(
            **common,
            page_title="页面没有找到",
            page_description="你访问的页面没有找到",
            canonical_url=page_url(site, f"{site['base_path']}/404.html"),
            body_class="not-found-page",
        ),
    )

    search_index = {
        "posts": [
            {
                "title": post.title,
                "url": post.url,
                "summary": post.summary,
                "category": post.category,
                "category_url": post.meta["category_url"],
                "tags": [tag["name"] for tag in post.tags],
                "date": post.date.strftime("%Y-%m-%d"),
                "content": post.plain_text,
            }
            for post in posts
        ]
    }
    write_html(
        DIST_DIR / "search-index.json",
        json.dumps(search_index, ensure_ascii=False, separators=(",", ":")),
    )

    for source, destination in (
        (STATIC_DIR, DIST_DIR / "assets"),
        (PUBLIC_DIR, DIST_DIR),
    ):
        if source == PUBLIC_DIR:
            for file in source.rglob("*"):
                if file.is_file():
                    target = destination / file.relative_to(source)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file, target)
        else:
            shutil.copytree(source, destination, dirs_exist_ok=True)

    pygments_css = HtmlFormatter(style="github-dark").get_style_defs(".highlight")
    write_html(DIST_DIR / "assets" / "pygments.css", pygments_css + "\n")

    write_html(DIST_DIR / "feed.xml", build_rss(site, posts))

    sitemap_paths = [
        f"{site['base_path']}/",
        f"{site['base_path']}/archives/",
        f"{site['base_path']}/tags/",
        f"{site['base_path']}/categories/",
        f"{site['base_path']}/about/",
    ]
    sitemap_paths.extend(post.url for post in posts)
    sitemap_paths.extend(tag["url"] for tag in tags)
    sitemap_paths.extend(category["url"] for category in categories)
    write_html(DIST_DIR / "sitemap.xml", build_sitemap(site, sitemap_paths))
    write_html(
        DIST_DIR / "robots.txt",
        f"User-agent: *\nAllow: /\nSitemap: {site['base_url']}{site['base_path']}/sitemap.xml\n",
    )
    write_html(
        DIST_DIR / "site.webmanifest",
        json.dumps(
            {
                "name": site["title"],
                "short_name": site["title"],
                "description": site["description"],
                "start_url": f"{site['base_path']}/",
                "display": "standalone",
                "background_color": "#f3efe6",
                "theme_color": "#b4482e",
                "icons": [
                    {
                        "src": f"{site['base_path']}/assets/images/site/favicon.svg",
                        "sizes": "any",
                        "type": "image/svg+xml",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    write_html(DIST_DIR / ".nojekyll", "")

    print(
        json.dumps(
            {
                "posts": len(posts),
                "tags": len(tags),
                "categories": len(categories),
                "images": len(list((DIST_DIR / "assets" / "images" / "legacy").glob("*"))),
                "output": str(DIST_DIR),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
