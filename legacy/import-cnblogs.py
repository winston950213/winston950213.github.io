#!/usr/bin/env python3
"""Import the cnblogs JSON backup into the Hexo/Shoka site.

The script is intentionally conservative:

* 41 cnblogs posts are represented by 28 new Markdown files and 13 existing
  posts. Existing posts are never overwritten; only their front-matter date is
  changed.
* The seven posts that only existed on the new site are included in the date
  redistribution, so the final archive contains 48 posts.
* Images are copied into ``shoka/source/images/cnblogs`` and referenced with
  site-local ``/images/cnblogs/...`` URLs.

Usage:

    python legacy/import-cnblogs.py --dry-run
    python legacy/import-cnblogs.py --write
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, time, timedelta
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup, Tag


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "shoka" / "source" / "_posts"
IMAGE_DIR = ROOT / "shoka" / "source" / "images" / "cnblogs"
PLAN_PATH = ROOT / "legacy" / "cnblogs-import-plan.json"
REPORT_PATH = ROOT / "legacy" / "cnblogs-import-report.json"

DEFAULT_BACKUP = Path(
    r"C:\Users\Administrator\Downloads"
    r"\cnblogs_blog_zhangxuel1ang.20261030111547"
)

ASSET_ROOTS = [
    Path(r"D:\test_code\blog_img_original2"),
    Path(r"D:\test_code\coderdogz-image-assets"),
    Path(r"D:\test_code\cnblogs-assets"),
]

# Blog ids already represented on the new site. Keeping these files avoids
# duplicating articles and preserves their existing permalinks.
DUPLICATE_FILES = {
    13867030: "2022-11-01-python-multithreading.md",
    14052487: "2022-11-01-python-video-watermark.md",
    14257791: "2022-11-02-bookmark-urls.md",
    14375396: "2022-11-04-frida-setup-py-egg-info.md",
    14257753: "2022-11-04-git-remote-origin-exists.md",
    14431784: "2022-11-04-kali-terminal-emulator.md",
    14257760: "2022-11-04-mitmproxy-brotlipy-wheel.md",
    14257775: "2022-11-04-mitmproxy-certificate-page.md",
    14257721: "2022-11-04-regex-negation.md",
    14407538: "2022-11-04-ubuntu-change-mirror.md",
    14370126: "2022-11-04-ubuntu-curl-libcurl4.md",
    14475753: "2022-11-04-ubuntu-neofetch-package.md",
    14372929: "2022-11-04-ubuntu-pip3-list-warning.md",
}

# These seven posts existed only on the new site. Their front-matter dates
# change during import, so keep the original dates here to make reruns stable.
SITE_ONLY_DATES = {
    "2021-03-23-android-reverse-environment.md": "2021-03-23T15:55:29+08:00",
    "2021-03-26-frida-rpc.md": "2021-03-26T15:55:06+08:00",
    "2021-04-22-yuedan-app-reverse.md": "2021-04-22T08:13:06+08:00",
    "2021-05-07-mobile-tv-app-reverse.md": "2021-05-07T12:22:10+08:00",
    "2021-05-10-sakura-app-reverse.md": "2021-05-10T17:12:53+08:00",
    "2021-05-19-http-illustrated-notes.md": "2021-05-19T07:27:53+08:00",
    "2021-05-23-packet-capture-notes.md": "2021-05-23T20:50:13+08:00",
}

MISSING_IMAGE_URLS = {
    "https://17637462979.github.io/post-images/1573050443410.png": {
        "basename": "1573050443410-placeholder.png",
        "alt": "Docker 常用命令截图（原图已失效，暂用 404 页面占位）",
        "placeholder_source": "legacy/assets/1573050443410-placeholder.png",
        "note": (
            "迁移说明：这篇文章中的原图 "
            "`https://17637462979.github.io/post-images/1573050443410.png` "
            "已经失效，当前使用 GitHub Pages 404 截图作为占位图。"
        ),
    }
}

START_DATE = datetime(2019, 1, 1, 12, 0, 0)
END_DATE = datetime(2025, 6, 30, 12, 0, 0)

FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.S)
DATE_LINE_RE = re.compile(r"(?m)^date:.*$")
GENERATED_POST_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-cnblogs-\d+\.md$")
MARKDOWN_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
HTML_IMAGE_RE = re.compile(
    r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.I
)


@dataclass
class ExistingPost:
    path: Path
    title: str
    date: datetime
    permalink: str


@dataclass
class Article:
    key: str
    title: str
    source_title: str
    source_date: datetime
    source_order: int
    kind: str
    blog_id: int | None = None
    source_path: Path | None = None
    body: str = field(default="", repr=False)
    target_date: datetime | None = None
    target_file: Path | None = None
    permalink: str = ""
    images: list[str] = field(default_factory=list)


def read_json_backup(backup_dir: Path) -> list[dict]:
    posts_path = backup_dir / "posts.json"
    if not posts_path.exists():
        raise FileNotFoundError(f"Backup file not found: {posts_path}")
    with posts_path.open(encoding="utf-8-sig") as handle:
        posts = json.load(handle)
    if not isinstance(posts, list) or not posts:
        raise ValueError(f"Unexpected posts.json structure: {posts_path}")
    return posts


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    match = FM_RE.match(text)
    if not match:
        return {}, text
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line or line.startswith((" ", "\t", "- ")):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values, text[match.end() :]


def parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=None)


def normalize_title(value: str) -> str:
    """Use typographic double quotes so titles are safe inside HTML attributes."""
    opening = True
    result: list[str] = []
    for character in html.unescape(value):
        if character == '"':
            result.append("“" if opening else "”")
            opening = not opening
        else:
            result.append(character)
    return "".join(result)


def load_existing_posts() -> list[ExistingPost]:
    posts: list[ExistingPost] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        # Generated import files are not site-only originals. Excluding them
        # keeps the importer idempotent after the first --write run.
        if GENERATED_POST_RE.match(path.name):
            continue
        text = path.read_text(encoding="utf-8-sig")
        front_matter, _ = parse_front_matter(text)
        title = front_matter.get("title", "")
        date_value = front_matter.get("date", "")
        if not title or not date_value:
            raise ValueError(f"Missing title/date in {path}")
        posts.append(
            ExistingPost(
                path=path,
                title=normalize_title(title),
                date=parse_datetime(date_value),
                permalink=front_matter.get("permalink", ""),
            )
        )
    return posts


def build_index() -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for root in ASSET_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                index.setdefault(path.name.lower(), []).append(path)
    return index


def resolve_asset(asset_index: dict[str, list[Path]], basename: str) -> Path:
    matches = asset_index.get(basename.lower(), [])
    if not matches:
        raise FileNotFoundError(f"Local image not found: {basename}")
    hashes = {hashlib.sha256(path.read_bytes()).hexdigest() for path in matches}
    if len(hashes) > 1:
        raise ValueError(
            "Conflicting local images with the same name: "
            + ", ".join(str(path) for path in matches)
        )
    return matches[0]


def url_basename(url: str) -> str:
    path = unquote(urlparse(url).path)
    return path.rstrip("/").split("/")[-1]


def copy_placeholder(target: Path, info: dict[str, str]) -> None:
    source = ROOT / info["placeholder_source"]
    if not source.exists():
        raise FileNotFoundError(f"Placeholder image not found: {source}")
    shutil.copy2(source, target)


def localize_images(
    body: str,
    article: Article,
    asset_index: dict[str, list[Path]],
    copy_images: bool,
) -> tuple[str, list[dict[str, str]]]:
    urls: list[str] = []
    for match in MARKDOWN_IMAGE_RE.finditer(body):
        urls.append(match.group(2))
    for match in HTML_IMAGE_RE.finditer(body):
        urls.append(match.group(1))

    unique_urls = list(dict.fromkeys(urls))
    localized: list[dict[str, str]] = []
    for url in unique_urls:
        if url in MISSING_IMAGE_URLS:
            info = MISSING_IMAGE_URLS[url]
            basename = info["basename"]
            local_url = f"/images/cnblogs/{basename}"
            if copy_images:
                IMAGE_DIR.mkdir(parents=True, exist_ok=True)
                target = IMAGE_DIR / basename
                if not target.exists():
                    copy_placeholder(target, info)
            localized.append(
                {
                    "source": url,
                    "basename": basename,
                    "local": local_url,
                    "status": "missing-placeholder",
                }
            )
            body = body.replace(url, local_url)
            continue

        basename = url_basename(url)
        if not basename:
            raise ValueError(f"Cannot determine image filename: {url}")
        source = resolve_asset(asset_index, basename)
        local_url = f"/images/cnblogs/{basename}"
        if copy_images:
            IMAGE_DIR.mkdir(parents=True, exist_ok=True)
            target = IMAGE_DIR / basename
            if target.exists():
                if hashlib.sha256(target.read_bytes()).digest() != hashlib.sha256(
                    source.read_bytes()
                ).digest():
                    raise ValueError(f"Image conflict: {target}")
            else:
                shutil.copy2(source, target)
        localized.append(
            {
                "source": url,
                "basename": basename,
                "local": local_url,
                "status": "localized",
            }
        )
        body = body.replace(url, local_url)

    article.images = [item["local"] for item in localized]
    return body, localized


def fix_markdown_fences(text: str) -> str:
    # One cnblogs article has the Python encoding declaration on the opening
    # fence itself. Move it into the code block and give the fence a language.
    text = re.sub(
        r"(?m)^```(#\s*-\*-.*)$",
        lambda match: "```python\n" + match.group(1),
        text,
    )
    return text


def prepare_markdown_body(
    body: str,
    article: Article,
    asset_index: dict[str, list[Path]],
    copy_images: bool,
) -> tuple[str, list[dict[str, str]]]:
    text = body.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\ufeff", "")
    text = html.unescape(text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    # Hexo uses this comment as the excerpt separator, so keep it.
    text = re.sub(r"<!--(?!\s*more\s*-->).*?-->", "", text, flags=re.S)
    text = fix_markdown_fences(text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    text, localized = localize_images(text, article, asset_index, copy_images)
    text = text.strip()

    missing = [item for item in localized if item["status"] == "missing-placeholder"]
    if missing:
        for item in missing:
            alt = MISSING_IMAGE_URLS[item["source"]]["alt"]
            text = text.replace(
                f"![]({item['local']})",
                f"![{alt}]({item['local']})",
            )
        notes = "\n\n".join(MISSING_IMAGE_URLS[item["source"]]["note"] for item in missing)
        text += f"\n\n---\n\n> {notes}\n"
    return text, localized


def image_markdown(src: str, alt: str = "") -> str:
    return f"![{alt}]({src})"


def paragraph_to_markdown(element: Tag) -> str:
    parts: list[str] = []
    for child in element.children:
        if isinstance(child, Tag):
            if child.name == "img":
                parts.append(image_markdown(child.get("src", ""), child.get("alt", "")))
            elif child.name == "br":
                parts.append("\n")
            else:
                parts.append(child.get_text(" ", strip=True))
        else:
            parts.append(str(child))
    return html.unescape("".join(parts)).strip()


def convert_first_post(body: str) -> str:
    soup = BeautifulSoup(body, "html.parser")
    paragraphs = [paragraph_to_markdown(p) for p in soup.find_all("p")]
    paragraphs = [paragraph for paragraph in paragraphs if paragraph]
    return "\n\n".join(paragraphs)


def convert_jsencrypt_post(body: str) -> str:
    soup = BeautifulSoup(body, "html.parser")
    preview = soup.find("div", class_="preview") or soup
    elements = preview.find_all(["h2", "li", "pre"], recursive=True)

    output: list[str] = []
    heading_count = 0
    list_count = 0
    code_count = 0
    for element in elements:
        if element.name == "li" and element.find_parent("li"):
            continue
        if element.name == "h2":
            heading_count += 1
            output.append(f"## {element.get_text(' ', strip=True)}")
        elif element.name == "li":
            list_count += 1
            output.append(f"- {element.get_text(' ', strip=True)}")
        elif element.name == "pre":
            code_count += 1
            code_element = element.find("code")
            code = code_element.get_text() if code_element else element.get_text()
            fence = "````"
            output.append(f"{fence}javascript\n{code.rstrip()}\n{fence}")

    if (heading_count, list_count, code_count) != (2, 2, 2):
        raise ValueError(
            "Unexpected JSencrypt HTML structure: "
            f"headings={heading_count}, list_items={list_count}, code_blocks={code_count}"
        )
    return "\n\n".join(output).strip()


def convert_html_post(post: dict) -> str:
    post_id = int(post["Id"])
    body = post.get("Body") or ""
    if post_id == 9240721:
        return convert_first_post(body)
    if post_id == 14290032:
        return convert_jsencrypt_post(body)
    raise ValueError(f"No HTML converter for post {post_id}")


def build_articles(
    posts: list[dict], existing_posts: list[ExistingPost]
) -> tuple[list[Article], list[ExistingPost]]:
    existing_by_name = {post.path.name: post for post in existing_posts}
    missing_duplicates = [
        filename
        for filename in DUPLICATE_FILES.values()
        if filename not in existing_by_name
    ]
    if missing_duplicates:
        raise FileNotFoundError(
            "Duplicate target files are missing: " + ", ".join(missing_duplicates)
        )

    articles: list[Article] = []
    for order, post in enumerate(posts):
        post_id = int(post["Id"])
        source_title = html.unescape(post["Title"] or "")
        source_date = parse_datetime(post["DateAdded"])
        if post_id in DUPLICATE_FILES:
            existing = existing_by_name[DUPLICATE_FILES[post_id]]
            articles.append(
                Article(
                    key=f"existing:{existing.path.name}",
                    title=existing.title,
                    source_title=source_title,
                    source_date=source_date,
                    source_order=order,
                    kind="duplicate",
                    blog_id=post_id,
                    source_path=existing.path,
                    permalink=existing.permalink,
                )
            )
        else:
            articles.append(
                Article(
                    key=f"cnblogs:{post_id}",
                    title=normalize_title(source_title),
                    source_title=source_title,
                    source_date=source_date,
                    source_order=order,
                    kind="new",
                    blog_id=post_id,
                    body=post.get("Body") or "",
                )
            )

    duplicate_paths = set(DUPLICATE_FILES.values())
    site_only = [
        post for post in existing_posts if post.path.name not in duplicate_paths
    ]
    for order, existing in enumerate(site_only):
        if existing.path.name not in SITE_ONLY_DATES:
            raise KeyError(f"Missing original date for site-only post: {existing.path}")
        articles.append(
            Article(
                key=f"site:{existing.path.name}",
                title=existing.title,
                source_title=existing.title,
                source_date=parse_datetime(SITE_ONLY_DATES[existing.path.name]),
                source_order=10_000 + order,
                kind="site",
                source_path=existing.path,
                permalink=existing.permalink,
            )
        )

    articles.sort(key=lambda item: (item.source_date, item.source_order, item.title))
    total_days = (END_DATE.date() - START_DATE.date()).days
    step = total_days / (len(articles) - 1)
    for index, article in enumerate(articles):
        offset = round(index * step)
        article.target_date = datetime.combine(
            START_DATE.date() + timedelta(days=offset), time(12, 0, 0)
        )
        if article.kind == "new":
            article.target_file = POSTS_DIR / (
                f"{article.target_date:%Y-%m-%d}-cnblogs-{article.blog_id}.md"
            )
            article.permalink = (
                f"{article.target_date:%Y/%m/%d}/cnblogs-{article.blog_id}/"
            )
    return articles, site_only


def build_plan(
    backup_dir: Path,
    articles: list[Article],
    site_only: list[ExistingPost],
) -> dict:
    return {
        "backup": backup_dir.name,
        "start": START_DATE.isoformat(),
        "end": END_DATE.isoformat(),
        "article_count": len(articles),
        "counts": {
            "new": sum(article.kind == "new" for article in articles),
            "duplicate": sum(article.kind == "duplicate" for article in articles),
            "site_only": sum(article.kind == "site" for article in articles),
            "images": sum(len(article.images) for article in articles),
        },
        "site_only": [post.path.name for post in site_only],
        "articles": [
            {
                "order": index + 1,
                "kind": article.kind,
                "blog_id": article.blog_id,
                "title": article.title,
                "source_title": article.source_title,
                "source_date": article.source_date.isoformat(sep=" "),
                "date": article.target_date.isoformat(sep=" "),
                "file": (
                    str(article.target_file.relative_to(ROOT))
                    if article.target_file
                    else str(article.source_path.relative_to(ROOT))
                ),
                "permalink": article.permalink,
            }
            for index, article in enumerate(articles)
        ],
    }


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_front_matter(article: Article) -> str:
    assert article.target_date is not None
    return "\n".join(
        [
            "---",
            f"title: {yaml_string(article.title)}",
            f"date: '{article.target_date:%Y-%m-%d %H:%M:%S}'",
            f"permalink: {article.permalink}",
            "categories:",
            "- 博客园",
            "tags:",
            "- 博客园",
            "comment: true",
            "fancybox: true",
            "---",
        ]
    )


def update_existing_date(path: Path, target_date: datetime) -> None:
    raw = path.read_bytes().decode("utf-8-sig")
    front_match = FM_RE.match(raw)
    if not front_match:
        raise ValueError(f"Missing front matter: {path}")
    date_match = DATE_LINE_RE.search(front_match.group(1))
    if not date_match:
        raise ValueError(f"Missing date line: {path}")
    start = front_match.start(1) + date_match.start()
    end = front_match.start(1) + date_match.end()
    replacement = f"date: '{target_date:%Y-%m-%d %H:%M:%S}'"
    updated = raw[:start] + replacement + raw[end:]
    path.write_bytes(updated.encode("utf-8"))


def write_new_post(article: Article, body: str) -> None:
    assert article.target_file is not None
    content = render_front_matter(article) + "\n\n" + body.rstrip() + "\n"
    with article.target_file.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def write_articles(
    posts: list[dict],
    articles: list[Article],
    asset_index: dict[str, list[Path]],
) -> dict:
    posts_by_id = {int(post["Id"]): post for post in posts}
    image_report: list[dict[str, str]] = []
    for article in articles:
        assert article.target_date is not None
        if article.kind == "new":
            post = posts_by_id[int(article.blog_id)]
            if post.get("IsMarkdown"):
                body, localized = prepare_markdown_body(
                    article.body, article, asset_index, copy_images=True
                )
            else:
                body = convert_html_post(post)
                body, localized = localize_images(
                    body, article, asset_index, copy_images=True
                )
                body = body.strip()
            write_new_post(article, body)
            for item in localized:
                item["article"] = article.title
                item["blog_id"] = str(article.blog_id)
                image_report.append(item)
        else:
            assert article.source_path is not None
            update_existing_date(article.source_path, article.target_date)

    missing = [
        item for item in image_report if item["status"] == "missing-placeholder"
    ]
    return {
        "new_posts": sum(article.kind == "new" for article in articles),
        "updated_posts": sum(article.kind != "new" for article in articles),
        "images_localized": sum(
            item["status"] == "localized" for item in image_report
        ),
        "missing_images": missing,
        "images": image_report,
    }


def print_plan(plan: dict) -> None:
    print(
        f"Articles: {plan['article_count']} "
        f"(new={plan['counts']['new']}, "
        f"duplicate={plan['counts']['duplicate']}, "
        f"site_only={plan['counts']['site_only']})"
    )
    print(f"Range: {plan['start']} -> {plan['end']}")
    for row in plan["articles"]:
        print(
            f"{row['order']:02d}  {row['date'][:10]}  "
            f"{row['kind']:<9}  {row['title']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", type=Path, default=DEFAULT_BACKUP)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.error("choose --dry-run or --write")

    posts = read_json_backup(args.backup)
    existing_posts = load_existing_posts()
    asset_index = build_index()
    articles, site_only = build_articles(posts, existing_posts)

    if len(articles) != 48:
        raise ValueError(f"Expected 48 articles, got {len(articles)}")
    if len(site_only) != 7:
        raise ValueError(f"Expected 7 site-only articles, got {len(site_only)}")

    plan = build_plan(args.backup, articles, site_only)
    print_plan(plan)

    if args.write:
        report = write_articles(posts, articles, asset_index)
        plan["counts"]["images"] = len(report["images"])
        REPORT_PATH.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(
            f"\nWrote {report['new_posts']} new posts, updated "
            f"{report['updated_posts']} existing posts, localized "
            f"{report['images_localized']} images."
        )
        if report["missing_images"]:
            print("Missing originals replaced with placeholders:")
            for item in report["missing_images"]:
                print(f"  - {item['source']} -> {item['local']}")

    PLAN_PATH.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"\nPlan: {PLAN_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
