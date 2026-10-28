(() => {
  "use strict";

  const base = document.body.dataset.base || "";
  const root = document.documentElement;
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const setTheme = (theme) => {
    root.dataset.theme = theme;
    try {
      localStorage.setItem("blog-theme", theme);
    } catch (_) {}
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === "ink" ? "#151412" : "#f3efe6";
  };

  document.querySelector(".theme-toggle")?.addEventListener("click", () => {
    setTheme(root.dataset.theme === "ink" ? "paper" : "ink");
  });

  const header = document.querySelector(".site-header");
  const progressBar = document.querySelector(".reading-progress span");
  const backToTop = document.querySelector(".back-to-top");
  const menuToggle = document.querySelector(".menu-toggle");
  const siteNav = document.querySelector(".site-nav");

  const updateScrollUI = () => {
    const scrollY = window.scrollY;
    header?.classList.toggle("is-scrolled", scrollY > 18);
    backToTop?.classList.toggle("is-visible", scrollY > 700);

    const articleBody = document.querySelector("#article-body");
    if (articleBody && progressBar) {
      const start = articleBody.offsetTop;
      const total = Math.max(1, articleBody.offsetHeight - window.innerHeight * 0.28);
      const progress = Math.min(1, Math.max(0, (scrollY - start + 80) / total));
      progressBar.style.width = `${(progress * 100).toFixed(2)}%`;
    }
  };

  updateScrollUI();
  window.addEventListener("scroll", updateScrollUI, { passive: true });
  window.addEventListener("resize", updateScrollUI, { passive: true });

  backToTop?.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
  });

  menuToggle?.addEventListener("click", () => {
    const open = siteNav?.classList.toggle("is-open") ?? false;
    menuToggle.setAttribute("aria-expanded", String(open));
    menuToggle.setAttribute("aria-label", open ? "关闭导航" : "打开导航");
  });

  siteNav?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      siteNav.classList.remove("is-open");
      menuToggle?.setAttribute("aria-expanded", "false");
    });
  });

  document.querySelectorAll("[data-copy-url]").forEach((button) => {
    button.addEventListener("click", async () => {
      const label = button.querySelector("span");
      const original = label?.textContent || "复制链接";
      try {
        await navigator.clipboard.writeText(button.dataset.copyUrl);
        if (label) label.textContent = "已复制";
      } catch (_) {
        if (label) label.textContent = "复制失败";
      }
      setTimeout(() => {
        if (label) label.textContent = original;
      }, 1600);
    });
  });

  document.querySelectorAll(".article-body .highlight").forEach((block) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "code-copy";
    button.textContent = "复制代码";
    button.addEventListener("click", async () => {
      const code = block.querySelector("code")?.textContent || "";
      try {
        await navigator.clipboard.writeText(code);
        button.textContent = "已复制";
      } catch (_) {
        button.textContent = "复制失败";
      }
      setTimeout(() => {
        button.textContent = "复制代码";
      }, 1400);
    });
    block.prepend(button);
  });

  const lightbox = document.createElement("div");
  lightbox.className = "image-lightbox";
  lightbox.hidden = true;
  lightbox.setAttribute("role", "dialog");
  lightbox.setAttribute("aria-label", "查看大图");
  lightbox.innerHTML = '<img alt="">';
  document.body.append(lightbox);
  const lightboxImage = lightbox.querySelector("img");

  document.querySelectorAll(".article-body img").forEach((image) => {
    image.addEventListener("click", () => {
      if (!lightboxImage) return;
      lightboxImage.src = image.currentSrc || image.src;
      lightboxImage.alt = image.alt || "文章插图";
      lightbox.hidden = false;
      document.body.style.overflow = "hidden";
    });
  });

  const closeLightbox = () => {
    lightbox.hidden = true;
    if (lightboxImage) lightboxImage.removeAttribute("src");
    document.body.style.overflow = "";
  };

  lightbox.addEventListener("click", closeLightbox);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !lightbox.hidden) closeLightbox();
  });

  const tocLinks = [...document.querySelectorAll(".toc a[href^='#']")];
  if (tocLinks.length) {
    const targets = tocLinks
      .map((link) => {
        const id = decodeURIComponent(link.getAttribute("href").slice(1));
        return { link, heading: document.getElementById(id) };
      })
      .filter((item) => item.heading);

    const setActive = () => {
      let active = targets[0];
      for (const item of targets) {
        if (item.heading.getBoundingClientRect().top <= 150) active = item;
      }
      targets.forEach((item) => item.link.classList.toggle("is-active", item === active));
    };

    setActive();
    window.addEventListener("scroll", setActive, { passive: true });
  }

  const dialog = document.querySelector("#search-dialog");
  const input = document.querySelector("#search-input");
  const resultsBox = document.querySelector("#search-results");
  if (!dialog || !input || !resultsBox) return;

  let searchIndex = null;
  let searchPromise = null;
  let activeIndex = -1;
  let currentResults = [];
  let returnFocus = null;

  const loadIndex = () => {
    if (searchIndex) return Promise.resolve(searchIndex);
    if (searchPromise) return searchPromise;
    searchPromise = fetch(`${base}/search-index.json`)
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((data) => {
        searchIndex = data.posts || [];
        return searchIndex;
      })
      .catch((error) => {
        resultsBox.textContent = "搜索索引加载失败，请稍后刷新重试。";
        throw error;
      });
    return searchPromise;
  };

  const scorePost = (post, terms) => {
    const title = post.title.toLowerCase();
    const summary = post.summary.toLowerCase();
    const tags = post.tags.join(" ").toLowerCase();
    const category = post.category.toLowerCase();
    const content = post.content.toLowerCase();
    let score = 0;

    for (const term of terms) {
      if (!`${title} ${summary} ${tags} ${category} ${content}`.includes(term)) return -1;
      if (title.includes(term)) score += 40;
      if (tags.includes(term)) score += 24;
      if (category.includes(term)) score += 10;
      if (summary.includes(term)) score += 8;
      score += Math.min(6, content.split(term).length - 1);
    }
    return score;
  };

  const makeResult = (post, index) => {
    const link = document.createElement("a");
    link.className = "search-result";
    link.href = post.url;
    link.dataset.index = String(index);

    const title = document.createElement("strong");
    title.textContent = post.title;
    const summary = document.createElement("p");
    summary.textContent = post.summary;
    const meta = document.createElement("small");
    meta.textContent = `${post.date} · ${post.category} · ${post.tags.slice(0, 3).map((tag) => `#${tag}`).join(" ")}`;
    link.append(title, summary, meta);
    return link;
  };

  const render = (posts) => {
    resultsBox.replaceChildren();
    activeIndex = -1;
    currentResults = posts.slice(0, 9);

    if (!currentResults.length) {
      const empty = document.createElement("div");
      empty.className = "search-empty";
      empty.textContent = "没有找到相关文章，换个关键词试试。";
      resultsBox.append(empty);
      return;
    }

    currentResults.forEach((post, index) => resultsBox.append(makeResult(post, index)));
    const first = resultsBox.querySelector(".search-result");
    if (first) {
      first.classList.add("is-active");
      activeIndex = 0;
    }
  };

  const runSearch = async () => {
    const query = input.value.trim().toLowerCase();
    const posts = await loadIndex();
    if (!query) {
      render(posts.slice(0, 6));
      return;
    }
    const terms = query.split(/\s+/).filter(Boolean);
    const matches = posts
      .map((post) => ({ post, score: scorePost(post, terms) }))
      .filter((item) => item.score >= 0)
      .sort((a, b) => b.score - a.score || b.post.date.localeCompare(a.post.date))
      .map((item) => item.post);
    render(matches);
  };

  const moveSelection = (direction) => {
    const items = [...resultsBox.querySelectorAll(".search-result")];
    if (!items.length) return;
    activeIndex = (activeIndex + direction + items.length) % items.length;
    items.forEach((item, index) => item.classList.toggle("is-active", index === activeIndex));
    items[activeIndex].scrollIntoView({ block: "nearest" });
  };

  const openSearch = async (trigger) => {
    returnFocus = trigger || document.activeElement;
    if (typeof dialog.showModal === "function") {
      if (!dialog.open) dialog.showModal();
    } else {
      dialog.setAttribute("open", "");
    }
    input.value = "";
    resultsBox.textContent = "正在载入索引…";
    setTimeout(() => input.focus(), 20);
    try {
      await loadIndex();
      render(searchIndex.slice(0, 6));
    } catch (_) {}
  };

  document.querySelectorAll(".search-trigger").forEach((trigger) => {
    trigger.addEventListener("click", () => openSearch(trigger));
  });

  dialog.querySelector(".search-close")?.addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", () => {
    document.body.style.overflow = "";
    if (returnFocus instanceof HTMLElement) returnFocus.focus();
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });

  input.addEventListener("input", () => {
    runSearch().catch(() => {});
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveSelection(1);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      moveSelection(-1);
    } else if (event.key === "Enter") {
      const selected = resultsBox.querySelector(".search-result.is-active");
      if (selected) {
        event.preventDefault();
        location.href = selected.href;
      }
    }
  });

  document.addEventListener("keydown", (event) => {
    const target = event.target;
    const typing = target instanceof HTMLElement &&
      (target.matches("input, textarea, select") || target.isContentEditable);
    if (!typing && (event.key === "/" || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k"))) {
      event.preventDefault();
      openSearch(document.activeElement);
    }
  });

  if (document.body.classList.contains("search-page")) {
    openSearch(document.querySelector(".search-trigger"));
  }
})();
