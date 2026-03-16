from __future__ import annotations

import html
import math
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
BLOG_INDEX = ROOT / "articles.html"


SPECIAL_WORDS = {
    "ai": "AI",
    "asp": "ASP",
    "net": ".NET",
    "sql": "SQL",
    "soap": "SOAP",
    "api": "API",
    "apis": "APIs",
    "core": "Core",
    "winforms": "WinForms",
}

TITLE_OVERRIDES = {
    "building-ai-assisted-engineering-workflows-that-100x-output": "Building AI-Assisted Engineering Workflows That 100x Output",
    "from-net-framework-to-asp-net-core-a-practical-migration-path": "From .NET Framework to ASP.NET Core, a Practical Migration Path",
    "how-ai-workflows-change-the-economics-of-software-delivery": "How AI Workflows Change the Economics of Software Delivery",
    "how-better-architecture-reduces-long-term-software-cost": "How Better Architecture Reduces Long-Term Software Cost",
    "how-to-refactor-a-monolith-into-safer-smaller-steps": "How to Refactor a Monolith into Safer, Smaller Steps",
    "how-to-update-critical-software-with-no-service-interruptions": "How to Update Critical Software With No Service Interruptions",
    "leaving-silverlight-behind-without-losing-business-knowledge": "Leaving Silverlight Behind Without Losing Business Knowledge",
    "logging-and-observability-for-legacy-applications": "Logging and Observability for Legacy Applications",
    "modern-authentication-upgrades-for-legacy-business-systems": "Modern Authentication Upgrades for Legacy Business Systems",
    "modernizing-front-ends-built-on-outdated-frameworks": "Modernizing Front Ends Built on Outdated Frameworks",
    "modernizing-net-framework-4-applications-without-breaking-the-business": "Modernizing .NET Framework 4 Applications Without Breaking the Business",
    "replacing-soap-services-without-rewriting-everything": "Replacing SOAP Services Without Rewriting Everything",
    "security-improvements-that-also-reduce-cost": "Security Improvements That Also Reduce Cost",
    "shipping-modernization-work-in-production-safe-slices": "Shipping Modernization Work in Production-Safe Slices",
    "sql-performance-tuning-as-a-business-lever": "SQL Performance Tuning as a Business Lever",
    "the-case-for-incremental-change-in-critical-systems": "The Case for Incremental Change in Critical Systems",
    "using-ai-to-eliminate-repetitive-engineering-work": "Using AI to Eliminate Repetitive Engineering Work",
    "what-to-do-with-aging-winforms-applications": "What to Do With Aging WinForms Applications",
    "why-faster-systems-cost-less-to-run": "Why Faster Systems Cost Less to Run",
    "why-senior-engineers-should-be-designing-automation-systems": "Why Senior Engineers Should Be Designing Automation Systems",
}

CATEGORY_OVERRIDES = {
    "why-faster-systems-cost-less-to-run": "Performance",
}

SECONDARY_TAGS = {
    "AI & Automation": "Workflow Design",
    "Modernization": "Legacy Upgrade",
    "Risk Reduction": "Safe Delivery",
    "Performance": "Efficiency",
    "Legacy UI": "Platform Strategy",
    "Integration": "System Boundaries",
    "Security": "Compliance",
    "Architecture": "Maintainability",
    "Databases": "Query Health",
    "Delivery": "Release Strategy",
    "Operations": "Observability",
    "Cost Savings": "Business Value",
}

MOJIBAKE_MAP = {
    "â€™": "'",
    "â€œ": '"',
    "â€": '"',
    "â€“": "-",
    "â€”": "-",
    "â€¦": "...",
    "Â": "",
}


@dataclass
class Post:
    slug: str
    title: str
    date: datetime
    category: str
    lead: str
    paragraphs: list[str]
    read_minutes: int
    output_name: str


def clean_text(text: str) -> str:
    text = text.replace("\ufeff", "")
    for bad, good in MOJIBAKE_MAP.items():
        text = text.replace(bad, good)
    return text.strip()


def title_from_slug(slug: str) -> str:
    if slug in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[slug]
    words = slug.split("-")
    rendered: list[str] = []
    i = 0
    while i < len(words):
        pair = "-".join(words[i : i + 3])
        if pair == "asp-net-core":
            rendered.append("ASP.NET Core")
            i += 3
            continue
        pair = "-".join(words[i : i + 2])
        if pair == "net-framework":
            rendered.append(".NET Framework")
            i += 2
            continue

        word = words[i]
        if word in SPECIAL_WORDS:
            rendered.append(SPECIAL_WORDS[word])
        elif word == "to":
            rendered.append("to")
        elif word in {"a", "an", "the", "for", "with", "of", "on", "in", "and", "or", "into", "without"} and rendered:
            rendered.append(word)
        else:
            rendered.append(word.capitalize())
        i += 1

    title = " ".join(rendered)
    title = title.replace(".NET Framework 4 Applications", ".NET Framework 4 Applications")
    title = title.replace(".NET Framework to ASP.NET Core", ".NET Framework to ASP.NET Core")
    return title


def category_from_slug(slug: str) -> str:
    if slug in CATEGORY_OVERRIDES:
        return CATEGORY_OVERRIDES[slug]
    if "ai" in slug:
        return "AI & Automation"
    if "authentication" in slug or "security" in slug:
        return "Security"
    if "sql" in slug:
        return "Databases"
    if "soap" in slug:
        return "Integration"
    if "winforms" in slug or "silverlight" in slug or "front-ends" in slug:
        return "Legacy UI"
    if "logging" in slug or "observability" in slug:
        return "Operations"
    if "architecture" in slug or "monolith" in slug:
        return "Architecture"
    if "faster-systems" in slug:
        return "Performance"
    if "service-interruptions" in slug or "incremental-change" in slug:
        return "Risk Reduction"
    if "production-safe" in slug:
        return "Delivery"
    if "cost" in slug:
        return "Cost Savings"
    return "Modernization"


def parse_post(path: Path) -> Post:
    raw = clean_text(path.read_text(encoding="utf-8"))
    blocks = [clean_text(block) for block in re.split(r"\r?\n\s*\r?\n", raw) if block.strip()]
    date = datetime.strptime(blocks[0], "%B %d, %Y")
    paragraphs = blocks[1:]
    lead = paragraphs[0]
    words = sum(len(paragraph.split()) for paragraph in paragraphs)
    read_minutes = max(2, math.ceil(words / 180))
    slug = path.stem
    return Post(
        slug=slug,
        title=title_from_slug(slug),
        date=date,
        category=category_from_slug(slug),
        lead=lead,
        paragraphs=paragraphs,
        read_minutes=read_minutes,
        output_name=f"blog-{slug}.html",
    )


def render_header(page_title: str, description: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(page_title)}</title>
  <meta name="description" content="{html.escape(description)}" />
  <link rel="stylesheet" href="assets/styles.css" />
</head>
<body>
  <div class="bg-orb orb-1" aria-hidden="true"></div>
  <div class="bg-orb orb-2" aria-hidden="true"></div>

  <header class="site-header" id="top">
    <a class="skip-link" href="#main">Skip to content</a>
    <div class="container header-inner">
      <a class="brand" href="index.html" aria-label="Derek Perez home">
        <span class="brand-mark" aria-hidden="true">DP</span>
        <span class="brand-copy">
          <strong>Derek Perez</strong>
          <span>Senior .NET Engineer &middot; Modernization Specialist &middot; AI-Augmented Developer</span>
        </span>
      </a>

      <nav class="desktop-nav" aria-label="Primary">
        <a href="about.html">About</a>
        <a href="projects.html">Projects</a>
        <a href="services.html">Services</a>
        <a href="articles.html">Blog</a>
        <a href="contact.html">Contact</a>
      </nav>

      <div class="header-actions">
        <button class="icon-btn theme-toggle" type="button" aria-label="Toggle color theme" data-theme-toggle>
          <span class="theme-dot"></span>
        </button>
        <a class="btn btn-sm btn-secondary hide-mobile" href="#resume">Resume</a>
        <button class="icon-btn mobile-menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu" data-menu-toggle>
          <span></span><span></span><span></span>
        </button>
      </div>
    </div>

    <div class="mobile-menu" id="mobile-menu" hidden>
      <div class="container mobile-menu-inner">
        <a href="about.html">About</a>
        <a href="projects.html">Projects</a>
        <a href="services.html">Services</a>
        <a href="articles.html">Blog</a>
        <a href="contact.html">Contact</a>
        <a href="#resume">Download Resume</a>
      </div>
    </div>
  </header>

  <main id="main">
"""


def render_footer() -> str:
    return """
  </main>

  <section class="resume-banner panel" id="resume">
    <div class="container resume-inner">
      <div>
        <p class="eyebrow">Resume</p>
        <h2>Need the concise version?</h2>
        <p class="muted">Download a summary of experience, technical expertise, and enterprise engineering work.</p>
      </div>
      <a class="btn btn-primary" href="#" aria-label="Download Derek Perez resume PDF">Download Resume</a>
    </div>
  </section>

  <footer class="site-footer">
    <div class="container footer-grid">
      <div>
        <h3>Derek Perez</h3>
        <p class="muted">Senior .NET engineer specializing in legacy modernization, performance optimization, scalable architecture, and AI-augmented software delivery.</p>
        <p class="footer-note">Built as a static portfolio and consulting showcase.</p>
      </div>

      <div>
        <h4>Navigate</h4>
        <ul class="footer-links">
          <li><a href="index.html">Home</a></li>
          <li><a href="about.html">About</a></li>
          <li><a href="projects.html">Projects</a></li>
          <li><a href="services.html">Services</a></li>
          <li><a href="articles.html">Blog</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>

      <div>
        <h4>Connect</h4>
        <ul class="footer-links">
          <li><a href="mailto:derekdperez.dev@gmail.com">derekdperez.dev@gmail.com</a></li>
          <li><a href="#">LinkedIn</a></li>
          <li><a href="#">GitHub</a></li>
          <li><a href="#">Resume PDF</a></li>
        </ul>
      </div>

      <div>
        <h4>Location</h4>
        <p class="muted">Florence, Massachusetts<br />Available for remote consulting and contract engineering.</p>
        <div class="badge-row">
          <span class="badge">Remote Friendly</span>
          <span class="badge">UTC -5</span>
        </div>
      </div>
    </div>
    <div class="container footer-bottom">
      <p>&copy; 2026 Derek Perez. All rights reserved.</p>
      <a href="#top">Back to top</a>
    </div>
  </footer>

  <button class="back-to-top" type="button" aria-label="Back to top" data-back-to-top>&uarr;</button>
  <div class="toast" aria-live="polite" data-toast hidden>Preview opened</div>
  <script src="assets/app.js" defer></script>
</body>
</html>
"""


def render_post_cards(posts: list[Post], current_slug: str | None = None, limit: int | None = None) -> str:
    items = [post for post in posts if post.slug != current_slug]
    if limit is not None:
        items = items[:limit]
    cards = []
    for post in items:
        cards.append(
            f"""          <article class="card project-card reveal">
            <div class="project-visual"><div class="mock-ui"></div></div>
            <div class="meta-row">
              <span class="badge">{html.escape(post.category)} &middot; {post.date.strftime("%B %d, %Y")}</span>
              <span class="badge">By Derek Perez</span>
            </div>
            <h3>{html.escape(post.title)}</h3>
            <p class="muted">{html.escape(post.lead)}</p>
            <a class="btn btn-secondary btn-sm" href="{post.output_name}">Read post</a>
          </article>"""
        )
    return "\n".join(cards)


def render_post_page(post: Post, posts: list[Post]) -> str:
    paragraph_html = "\n".join(
        f"        <section class=\"card reveal\"><p>{html.escape(paragraph)}</p></section>"
        for paragraph in post.paragraphs[1:]
    )
    recent_posts = render_post_cards(posts, current_slug=post.slug, limit=3)
    description = post.lead[:150]
    return (
        render_header(f"{post.title} | Derek Perez", description)
        + f"""    <section class="article-hero">
      <div class="container reveal">
        <div class="breadcrumbs"><a href="index.html">Home</a> / <a href="articles.html">Blog</a> / <span>{html.escape(post.title)}</span></div>
        <p class="eyebrow" style="margin-top:1rem">Blog Post</p>
        <h1>{html.escape(post.title)}</h1>
        <p class="lead">{html.escape(post.lead)}</p>
        <div class="meta-row muted">
          <span>By Derek Perez</span>
          <span>{post.date.strftime("%B %d, %Y")}</span>
          <span>{post.read_minutes} min read</span>
          <span>{html.escape(post.category)}</span>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container article-layout">
        <aside class="sticky-aside reveal">
          <div class="card">
            <h3>Post Snapshot</h3>
            <div class="footer-links">
              <a href="articles.html">Back to blog</a>
              <span>{post.date.strftime("%B %d, %Y")}</span>
              <span>{post.read_minutes} minute read</span>
              <span>{html.escape(post.category)}</span>
            </div>
            <div class="badge-row" style="margin-top:1rem">
              <span class="badge">{html.escape(post.category)}</span>
              <span class="badge">{html.escape(SECONDARY_TAGS.get(post.category, "Software Delivery"))}</span>
            </div>
          </div>
        </aside>

        <article class="grid">
          <section class="card reveal">
            <p>{html.escape(post.paragraphs[0])}</p>
          </section>
{paragraph_html}
          <section class="card reveal">
            <h2>More from the blog</h2>
            <div class="three-col">
{recent_posts}
            </div>
          </section>
        </article>
      </div>
    </section>
"""
        + render_footer()
    )


def render_blog_index(existing: str, posts: list[Post]) -> str:
    cards = render_post_cards(posts)
    start_marker = '        <div class="article-grid three-col" style="margin-top:1.5rem">'
    start = existing.index(start_marker)
    end = existing.index("        </div>\n      </div>\n    </section>", start)
    replacement = start_marker + "\n\n" + cards + "\n\n"
    updated = existing[:start] + replacement + existing[end:]
    updated = updated.replace("  <title>Blog | Derek Perez</title>", "  <title>Blog | Derek Perez</title>")
    return updated


def main() -> None:
    posts = sorted((parse_post(path) for path in POSTS_DIR.glob("*.txt")), key=lambda post: post.date, reverse=True)

    for post in posts:
        output_path = ROOT / post.output_name
        output_path.write_text(render_post_page(post, posts), encoding="utf-8")

    blog_index = BLOG_INDEX.read_text(encoding="utf-8")
    BLOG_INDEX.write_text(render_blog_index(blog_index, posts), encoding="utf-8")


if __name__ == "__main__":
    main()
