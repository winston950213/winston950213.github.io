#!/usr/bin/env python3
"""Import the 2021-2022 Hexo articles into editable Markdown.

The JSON Feed is the authoritative snapshot of the old site's post bodies.
This script also verifies each item against the generated article page when
``--legacy-site`` is supplied, localizes linked images, and writes a migration
report.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse
from zoneinfo import ZoneInfo

import requests
import yaml
from bs4 import BeautifulSoup
from markdownify import markdownify
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FEED_PATH = ROOT / "legacy" / "feed.json"
POSTS_DIR = ROOT / "content" / "posts"
IMAGE_DIR = ROOT / "public" / "assets" / "images" / "legacy"
REPORT_PATH = ROOT / "legacy" / "migration-report.json"

TITLE_OVERRIDES = {
    "https://coderdogz.github.io/2022/11/02/网址备忘/": "网址备忘",
    "https://coderdogz.github.io/2022/10/31/python多线程学习/": "Python 多线程学习",
    "https://coderdogz.github.io/2022/10/31/python为视频添加水印/": "Python 为视频添加水印",
    "https://coderdogz.github.io/2021/05/19/再读-图解HTTP/": "再读《图解 HTTP》",
    "https://coderdogz.github.io/2021/03/26/frida-rpc-学习/": "Frida RPC 学习",
}

SLUGS = {
    "正则表达式反选": "regex-negation",
    "git报错：-fatal-remote-origin-already-exists": "git-remote-origin-exists",
    "win10安装mitmproxy报错-Failed-building-wheel-for-brotlipy": "mitmproxy-brotlipy-wheel",
    "win10安装mitmproxy，成功之后访问mitm-it出现不了下载证书页面": "mitmproxy-certificate-page",
    "Ubuntu安装curl报错：软件包有未满足的依赖关系：-curl-依赖-libcurl4-7-58-0-2ubuntu3-10": "ubuntu-curl-libcurl4",
    "linux-ubuntu-pip3-list-出现警告": "ubuntu-pip3-list-warning",
    "Command-python-setup-py-egg-info-failed-with-error-code-1-in-tmp-pip-build-thtq7d55-frida": "frida-setup-py-egg-info",
    "Ubuntu换源": "ubuntu-change-mirror",
    "Kali-Linux-Failed-to-launch-preferred-application-for-category-TerminalEmulator-and-all-files-missing": "kali-terminal-emulator",
    "E-Unable-to-locate-package-neofetch": "ubuntu-neofetch-package",
    "网址备忘": "bookmark-urls",
    "python多线程学习": "python-multithreading",
    "python为视频添加水印": "python-video-watermark",
    "抓包总结记录": "packet-capture-notes",
    "再读-图解HTTP": "http-illustrated-notes",
    "樱花": "sakura-app-reverse",
    "移动TV": "mobile-tv-app-reverse",
    "约单": "yuedan-app-reverse",
    "frida-rpc-学习": "frida-rpc",
    "逆向环境搭建": "android-reverse-environment",
}

SUMMARY_OVERRIDES = {
    "regex-negation": "用 bool() 简化正则 search 判断，并记录一种反向匹配的写法。",
    "git-remote-origin-exists": "两步处理 Git 远程仓库已存在时的 fatal 报错。",
    "mitmproxy-brotlipy-wheel": "在 Windows 10 安装 mitmproxy 时，解决 brotlipy 构建失败。",
    "mitmproxy-certificate-page": "排查 mitm.it 证书下载页无法打开的问题。",
    "ubuntu-curl-libcurl4": "处理 Ubuntu 安装 curl 时 libcurl4 版本依赖冲突。",
    "ubuntu-pip3-list-warning": "定位并清理 pip3 list 输出中的弃用警告。",
    "frida-setup-py-egg-info": "通过升级 setuptools 解决 Frida 安装阶段的 egg_info 报错。",
    "ubuntu-change-mirror": "以清华源为例，记录 Ubuntu 软件源切换步骤。",
    "kali-terminal-emulator": "恢复 Kali Linux 中 TerminalEmulator 默认终端配置。",
    "ubuntu-neofetch-package": "为 Ubuntu 16.04 补齐软件源后安装 neofetch。",
    "bookmark-urls": "整理日常常用网址与工具入口。",
    "python-multithreading": "Python 多线程学习的代码与要点整理。",
    "python-video-watermark": "使用 Python 为视频批量添加水印。",
    "packet-capture-notes": "从网络基础到工具配置，整理移动端抓包与证书处理经验。",
    "http-illustrated-notes": "《图解 HTTP》的阅读笔记与网络知识梳理。",
    "sakura-app-reverse": "一次围绕樱花 App 的安卓逆向与抓包记录。",
    "mobile-tv-app-reverse": "移动 TV 客户端逆向分析过程。",
    "yuedan-app-reverse": "约单 App 的 Frida 与安卓逆向实战记录。",
    "frida-rpc": "Frida RPC 开发环境、主动调用与内网穿透笔记。",
    "android-reverse-environment": "基于 Kali Linux 搭建安卓逆向环境的完整备忘。",
}

CATEGORIES = {"操作备忘", "编程语言", "读书笔记", "逆向学习"}
ZH_TIMEZONE = ZoneInfo("Asia/Shanghai")


def slug_from_legacy_url(url: str) -> str:
    path = unquote(urlparse(url).path).strip("/")
    key = path.split("/", 3)[-1] if path.count("/") >= 3 else path
    if key not in SLUGS:
        raise KeyError(f"No slug mapping for {key!r} ({url})")
    return SLUGS[key]


def legacy_path_from_url(url: str) -> str:
    return unquote(urlparse(url).path)


def clean_title(item: dict[str, object]) -> str:
    url = str(item["id"]).replace("http://example.com", "https://coderdogz.github.io")
    title = str(item["title"])
    title = TITLE_OVERRIDES.get(url, title)
    return re.sub(r"\.md$", "", title, flags=re.IGNORECASE).strip()


def decode_exturls(soup: BeautifulSoup) -> None:
    for span in soup.select("span.exturl[data-url]"):
        try:
            url = base64.b64decode(str(span["data-url"])).decode("utf-8")
        except Exception:
            continue
        anchor = soup.new_tag("a", href=url)
        anchor.string = span.get_text(" ", strip=True) or url
        span.replace_with(anchor)


def replace_code_blocks(soup: BeautifulSoup, code_blocks: list[str]) -> None:
    for index, figure in enumerate(soup.select("figure.highlight")):
        classes = [str(value) for value in figure.get("class", [])]
        language = next((value for value in classes if value != "highlight"), "")
        language = {
            "plaintext": "text",
            "sh": "bash",
            "js": "javascript",
        }.get(language, language)

        code_cell = figure.select_one("td.code pre")
        pre = code_cell or figure.find("pre")
        lines = [line.get_text() for line in pre.select("span.line")] if pre else []
        code = "\n".join(lines) if lines else (pre.get_text("\n") if pre else "")
        code = code.rstrip("\n")
        fences = "```"
        while fences in code:
            fences += "`"
        code_blocks.append(f"{fences}{language}\n{code}\n{fences}")

        token = soup.new_string(f"\n\n@@CODE_BLOCK_{index}@@\n\n")
        # Some legacy posts wrapped the generated <figure> in a stray
        # <pre><code> pair, producing invalid nested fences. Remove that
        # wrapper while replacing the original code block.
        wrapper = figure.find_parent(["pre", "code"])
        pre_wrapper = figure.find_parent("pre")
        if pre_wrapper is not None:
            figure.decompose()
            pre_wrapper.replace_with(token)
        elif wrapper is not None:
            figure.decompose()
            wrapper.replace_with(token)
        else:
            figure.replace_with(token)


def replace_task_lists(soup: BeautifulSoup, task_lists: list[str]) -> None:
    for index, task_list in enumerate(soup.select("ul.task-list")):
        lines = []
        for item in task_list.select(":scope > li"):
            checkbox = item.find("input", {"type": "checkbox"})
            checked = bool(checkbox and checkbox.has_attr("checked"))
            text = re.sub(r"\s+", " ", item.get_text(" ", strip=True)).strip()
            for label in item.select("label"):
                label.decompose()
            lines.append(f"- [{'x' if checked else ' '}] {text}")
        task_lists.append("\n".join(lines))
        task_list.replace_with(soup.new_string(f"\n\n@@TASK_LIST_{index}@@\n\n"))


def localize_images(
    soup: BeautifulSoup,
    image_urls: list[str],
    image_lookup: dict[str, str],
) -> None:
    for image in soup.find_all("img"):
        source = image.get("src") or image.get("data-src") or image.get("data-original")
        if not source:
            continue
        source = str(source)
        image_urls.append(source)
        image["src"] = image_lookup[source]
        if image.get("data-src"):
            del image["data-src"]
        if not image.get("alt"):
            image["alt"] = "文章插图"


def html_to_markdown(
    html: str,
    image_urls: list[str],
    image_lookup: dict[str, str],
) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup.select("#more"):
        tag.decompose()
    for anchor in soup.select("h1 a.anchor, h2 a.anchor, h3 a.anchor, h4 a.anchor, h5 a.anchor"):
        anchor.decompose()

    # The article title is the page H1, so body-level H1s become H2s.
    for heading in soup.find_all("h1"):
        heading.name = "h2"

    # A couple of posts stored literal heading HTML in paragraph text.
    for paragraph in soup.find_all("p"):
        text = paragraph.get_text(" ", strip=True)
        match = re.fullmatch(r"<h([1-6])(?:\s+[^>]*)?>\s*(.*?)\s*</h\1>", text)
        if match:
            level = max(2, int(match.group(1)))
            heading = soup.new_tag(f"h{level}")
            heading.string = re.sub(r"\s+", " ", match.group(2)).strip()
            paragraph.replace_with(heading)

    decode_exturls(soup)
    localize_images(soup, image_urls, image_lookup)

    code_blocks: list[str] = []
    replace_code_blocks(soup, code_blocks)

    task_lists: list[str] = []
    replace_task_lists(soup, task_lists)

    for caption in soup.select("figcaption"):
        caption.insert_before(soup.new_string("\n\n> "))
        caption.insert_after(soup.new_string("\n\n"))

    raw = str(soup)
    raw = re.sub(r"<p>\s*(@@(?:CODE_BLOCK|TASK_LIST)_\d+@@)\s*</p>", r"\1", raw)
    markdown = markdownify(
        raw,
        heading_style="ATX",
        bullets="-",
        strong_em_symbol="*",
        escape_asterisks=False,
        escape_underscores=False,
    )

    for index, block in enumerate(code_blocks):
        markdown = markdown.replace(f"@@CODE_BLOCK_{index}@@", block)
    for index, block in enumerate(task_lists):
        markdown = markdown.replace(f"@@TASK_LIST_{index}@@", block)

    markdown = markdown.replace("\r\n", "\n")
    markdown = re.sub(r"[ \t]+\n", "\n", markdown)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    markdown = re.sub(r"@@(?:CODE_BLOCK|TASK_LIST)_\d+@@", "", markdown)
    # A code placeholder embedded in a list can lose its leading newline.
    markdown = re.sub(r"(?<![\n`])(```[A-Za-z0-9_+\-]*\n)", r"\n\n\1", markdown)

    lines = markdown.split("\n")
    normalized_lines: list[str] = []
    inside_fence = False
    for line in lines:
        stripped = line.strip()
        is_closing_fence = inside_fence and re.fullmatch(r"`{3,}", stripped)
        is_opening_fence = not inside_fence and re.match(r"`{3,}[^`]*$", stripped)
        if is_opening_fence:
            if normalized_lines and normalized_lines[-1].strip():
                normalized_lines.append("")
            inside_fence = True
        elif is_closing_fence:
            inside_fence = False
        normalized_lines.append(line)
    markdown = "\n".join(normalized_lines)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip() + "\n"


def get_image_filename(url: str) -> str:
    return Path(unquote(urlparse(url).path)).name


def download_image(url: str, destination: Path, proxy: str | None) -> None:
    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = requests.get(
        url,
        timeout=45,
        proxies=proxies,
        headers={"User-Agent": "Mozilla/5.0 coderdogz-blog-migration"},
    )
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if not content_type.startswith("image/"):
        raise ValueError(f"Expected image from {url}, got {content_type!r}")
    destination.write_bytes(response.content)


def validate_image(path: Path) -> None:
    if path.stat().st_size < 100:
        raise ValueError(f"Image is unexpectedly small: {path}")
    with Image.open(path) as image:
        image.verify()


def normalized_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    return re.sub(r"\s+", "", soup.get_text(" ", strip=True))


def verify_against_legacy_site(
    item: dict[str, object],
    legacy_site: Path,
) -> dict[str, object]:
    path = unquote(urlparse(str(item["id"])).path).strip("/")
    page_path = legacy_site / path / "index.html"
    if not page_path.exists():
        return {"path": str(page_path), "exists": False}

    soup = BeautifulSoup(page_path.read_text(encoding="utf-8"), "lxml")
    body = soup.select_one("article.post .body.md")
    if body is None:
        return {"path": str(page_path), "exists": True, "has_body": False}

    feed_text = normalized_text(str(item["content_html"]))
    page_text = normalized_text(str(body))
    overlap = 0
    for length in (200, 100, 60, 40):
        probe = feed_text[:length]
        if probe and probe in page_text:
            overlap = length
            break
    return {
        "path": page_path.relative_to(legacy_site).as_posix(),
        "exists": True,
        "has_body": True,
        "feed_text_length": len(feed_text),
        "page_text_length": len(page_text),
        "opening_text_verified": overlap > 0,
    }


def yaml_frontmatter(metadata: dict[str, object]) -> str:
    payload = yaml.safe_dump(
        metadata,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=1000,
    ).strip()
    return f"---\n{payload}\n---\n\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-site", type=Path)
    parser.add_argument("--asset-dir", type=Path, action="append", default=[])
    parser.add_argument("--proxy")
    args = parser.parse_args()

    feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
    items = feed["items"]
    if len(items) != 20:
        raise ValueError(f"Expected 20 legacy posts, found {len(items)}")

    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    report_items: list[dict[str, object]] = []
    all_image_urls: list[str] = []
    image_lookup: dict[str, str] = {}

    for item in items:
        item = dict(item)
        item["id"] = str(item["id"]).replace("http://example.com", "https://coderdogz.github.io")
        slug = slug_from_legacy_url(item["id"])
        title = clean_title(item)
        tags = [str(value) for value in item.get("tags", [])]
        category = tags[0] if tags and tags[0] in CATEGORIES else "技术笔记"
        post_tags = [value for value in tags if value != category]
        published = datetime.fromisoformat(str(item["date_published"])).astimezone(ZH_TIMEZONE)

        image_urls: list[str] = []
        # This pass only gathers URLs so every asset can be prepared before
        # Markdown is generated with the final local paths.
        preview_soup = BeautifulSoup(str(item["content_html"]), "lxml")
        for image in preview_soup.find_all("img"):
            source = image.get("src") or image.get("data-src") or image.get("data-original")
            if source:
                all_image_urls.append(str(source))

        metadata = {
            "title": title,
            "slug": slug,
            "date": published.isoformat(timespec="seconds"),
            "category": category,
            "tags": post_tags,
            "summary": SUMMARY_OVERRIDES[slug],
            "legacy_path": legacy_path_from_url(item["id"]),
            "legacy_url": item["id"],
            "featured": slug == "bookmark-urls",
        }
        report_items.append(
            {
                "slug": slug,
                "title": title,
                "date": published.date().isoformat(),
                "legacy_url": item["id"],
                "category": category,
                "tags": post_tags,
                "image_count": len(image_urls),
                "verification": (
                    verify_against_legacy_site(item, args.legacy_site)
                    if args.legacy_site
                    else None
                ),
            }
        )

    # Resolve filename collisions between the two historical image hosts.
    url_by_filename: dict[str, set[str]] = {}
    for url in all_image_urls:
        url_by_filename.setdefault(get_image_filename(url), set()).add(url)

    for url in sorted(set(all_image_urls)):
        original_name = get_image_filename(url)
        filename = original_name
        if len(url_by_filename[original_name]) > 1:
            digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
            filename = f"{Path(original_name).stem}-{digest}{Path(original_name).suffix}"
        image_lookup[url] = f"/blog/assets/images/legacy/{filename}"

    asset_dirs = [path for path in args.asset_dir if path.exists()]
    copied = 0
    downloaded = 0
    reused = 0
    available_locally = 0
    for url, local_path in image_lookup.items():
        filename = Path(local_path).name
        destination = IMAGE_DIR / filename
        original_name = get_image_filename(url)
        source_path = next(
            (asset_dir / original_name for asset_dir in asset_dirs if (asset_dir / original_name).exists()),
            None,
        )
        if source_path:
            available_locally += 1
        if destination.exists():
            validate_image(destination)
            reused += 1
            continue
        if source_path:
            destination.write_bytes(source_path.read_bytes())
            copied += 1
        else:
            download_image(url, destination, args.proxy)
            downloaded += 1
        validate_image(destination)

    for item, report_item in zip(items, report_items):
        item = dict(item)
        item["id"] = str(item["id"]).replace("http://example.com", "https://coderdogz.github.io")
        slug = slug_from_legacy_url(item["id"])
        title = clean_title(item)
        tags = [str(value) for value in item.get("tags", [])]
        category = tags[0] if tags and tags[0] in CATEGORIES else "技术笔记"
        post_tags = [value for value in tags if value != category]
        published = datetime.fromisoformat(str(item["date_published"])).astimezone(ZH_TIMEZONE)
        image_urls: list[str] = []
        body = html_to_markdown(str(item["content_html"]), image_urls, image_lookup)
        metadata = {
            "title": title,
            "slug": slug,
            "date": published.isoformat(timespec="seconds"),
            "category": category,
            "tags": post_tags,
            "summary": SUMMARY_OVERRIDES[slug],
            "legacy_path": legacy_path_from_url(item["id"]),
            "legacy_url": item["id"],
            "featured": slug == "bookmark-urls",
        }
        post_path = POSTS_DIR / f"{published.date().isoformat()}-{slug}.md"
        post_path.write_text(
            yaml_frontmatter(metadata) + body,
            encoding="utf-8",
            newline="\n",
        )
        report_item["markdown_file"] = post_path.relative_to(ROOT).as_posix()
        report_item["image_count"] = len(image_urls)
        report_item["markdown_chars"] = len(body)

    report = {
        "source_repository": "https://github.com/coderdogz/coderdogz.github.io",
        "source_site": "https://coderdogz.github.io/",
        "migrated_on": datetime.now(ZH_TIMEZONE).date().isoformat(),
        "post_count": len(items),
        "unique_image_count": len(image_lookup),
        "images_reused_locally": reused,
        "images_available_from_local_repositories": available_locally,
        "images_copied_from_local_repositories": copied,
        "images_downloaded_during_import": downloaded,
        "image_hosts": dict(Counter(urlparse(url).netloc for url in image_lookup)),
        "articles": report_items,
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(
        {
            "posts": report["post_count"],
            "images": report["unique_image_count"],
            "images_reused": reused,
            "images_available_locally": available_locally,
            "images_copied": copied,
            "images_downloaded": downloaded,
            "report": str(REPORT_PATH),
        },
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
