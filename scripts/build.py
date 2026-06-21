"""Static Site Generator for Casa Inteligente affiliate site."""

import os
import re
import json
import shutil
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from email.utils import formatdate

import yaml
import markdown as md_lib
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUTPUT = ROOT / "output"
TEMPLATES = SRC / "templates"
CONTENT = SRC / "content"
STATIC = SRC / "static"

SITE_NAME = "Casa Inteligente PT"
SITE_URL = "https://casainteligente.pt"
SITE_DESCRIPTION = "Guias, reviews e comparações de produtos para casa inteligente. Reviews honestas de Amazon Alexa, Google Home, Xiaomi, Aqara e mais."
SITE_AUTHOR = "Equipa Casa Inteligente PT"
SITE_EMAIL = "ola@casainteligente.pt"

PER_PAGE = 12

ROOT_DIR = ROOT
DATA_DIR = ROOT / "data"
PRICES_FILE = DATA_DIR / "prices.json"


def load_price_data():
    if PRICES_FILE.exists():
        return json.loads(PRICES_FILE.read_text(encoding="utf-8"))
    return {"products": {}, "last_updated": None}


def extract_asin(url):
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    return match.group(1) if match else None


def find_product_for_post(post, price_data):
    asin = extract_asin(post.get("affiliate_link", ""))
    if not asin:
        return None
    for pid, info in price_data.get("products", {}).items():
        if info.get("asin") == asin:
            return pid
    return None

env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)

def parse_frontmatter(filepath):
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        return {"meta": {}, "body": content}
    meta = yaml.safe_load(match.group(1))
    body = match.group(2).strip()
    return {"meta": meta or {}, "body": body}

def md_to_html(text):
    return md_lib.markdown(
        text,
        extensions=["extra", "codehilite", "toc", "sane_lists"],
    )

def read_time(text, wpm=200):
    words = len(text.split())
    return max(1, round(words / wpm))

def get_category_slug(category):
    slug_map = {
        "Guias": "guias",
        "Reviews": "reviews",
        "Comparações": "comparacoes",
        "Guia": "guias",
        "Review": "reviews",
        "Comparação": "comparacoes",
    }
    return slug_map.get(category, category.lower().replace(" ", "-"))

def load_all_posts():
    posts = []
    price_data = load_price_data()
    for ext in ["md", "mdx"]:
        for filepath in sorted(CONTENT.rglob(f"*.{ext}")):
            parsed = parse_frontmatter(filepath)
            meta = parsed["meta"]
            html_body = md_to_html(parsed["body"])
            category = meta.get("category", "Geral")
            category_slug = get_category_slug(category)
            slug = filepath.stem
            url = f"/{category_slug}/{slug}/"
            date = meta.get("date", datetime.date.today())
            if isinstance(date, (datetime.date, datetime.datetime)):
                date_str = date.strftime("%d/%m/%Y") if isinstance(date, datetime.date) else date.strftime("%d/%m/%Y")
                date_iso = date.isoformat() if isinstance(date, datetime.date) else date.date().isoformat()
            else:
                try:
                    d = datetime.date.fromisoformat(str(date)[:10])
                    date_str = d.strftime("%d/%m/%Y")
                    date_iso = d.isoformat()
                except (ValueError, TypeError):
                    date_str = str(date)
                    date_iso = str(date)

            affiliate_link = meta.get("affiliate_link", "")
            product_id = find_product_for_post(meta, price_data)

            post = {
                "title": meta.get("title", filepath.stem.replace("-", " ").title()),
                "excerpt": meta.get("excerpt", ""),
                "content": html_body,
                "date": date_str,
                "date_iso": date_iso,
                "updated": meta.get("updated", ""),
                "author": meta.get("author", SITE_AUTHOR),
                "category": category,
                "category_slug": category_slug,
                "url": url,
                "image": meta.get("image", "default.jpg"),
                "rating": meta.get("rating"),
                "read_time": read_time(parsed["body"]),
                "featured": meta.get("featured", False),
                "affiliate_link": affiliate_link,
                "affiliate_disclosure": meta.get(
                    "affiliate_disclosure",
                    "Este artigo contém links de afiliados. Poderemos receber uma comissão por compras efetuadas através destes links, sem custo adicional para si.",
                ),
                "cta_text": meta.get("cta_text", ""),
                "tags": meta.get("tags", []),
                "product_id": product_id,
                "faq": meta.get("faq", []),
                "filepath": filepath,
            }

            if product_id and product_id in price_data.get("products", {}):
                product_info = price_data["products"][product_id]
                post["price_history"] = product_info.get("history", [])
                post["price_currency"] = product_info.get("currency", "EUR")
                post["price_current"] = post["price_history"][-1]["price"] if post["price_history"] else None
                post["price_min"] = min(p["price"] for p in post["price_history"]) if post["price_history"] else None
                post["price_max"] = max(p["price"] for p in post["price_history"]) if post["price_history"] else None

            posts.append(post)
    posts.sort(key=lambda p: p["date_iso"], reverse=True)
    return posts

def make_schema(schema_type, extra=None):
    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": SITE_NAME,
        "url": SITE_URL,
        "description": SITE_DESCRIPTION,
    }
    if extra:
        schema.update(extra)
    return json.dumps(schema, indent=4, ensure_ascii=False)

def render_page(template_name, output_path, schema=None, **context):
    template = env.get_template(template_name)
    if schema is None:
        schema = make_schema("WebSite")
    html = template.render(
        site_name=SITE_NAME,
        site_url=SITE_URL,
        site_description=SITE_DESCRIPTION,
        page_url=str(output_path),
        build_year=datetime.date.today().year,
        page_schema=schema,
        **context,
    )
    output_path = OUTPUT / output_path.lstrip("/")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix == "":
        output_path = output_path / "index.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path

def generate_index(posts):
    featured = next((p for p in posts if p["featured"]), None)
    guides = [p for p in posts if p["category_slug"] == "guias"][:6]
    reviews = [p for p in posts if p["category_slug"] == "reviews"][:6]
    comparisons = [p for p in posts if p["category_slug"] == "comparacoes"][:6]
    schema = make_schema("WebSite", {
        "url": SITE_URL,
        "potentialAction": {
            "@type": "SearchAction",
            "target": SITE_URL + "/?s={search_term}",
            "query-input": "required name=search_term"
        }
    })
    render_page("index.html", "/", schema=schema, featured_post=featured, guides=guides, reviews=reviews, comparisons=comparisons)

def generate_pages(posts):
    pages_data = [
        ("sobre", "about.html", "Sobre Nós"),
        ("privacidade", "privacy.html", "Política de Privacidade"),
        ("contacto", "contact.html", "Contacto"),
    ]
    for slug, template, title in pages_data:
        schema = make_schema("WebPage", {"name": title, "url": f"{SITE_URL}/{slug}/"})
        render_page(template, f"/{slug}/", schema=schema)

def generate_category_pages(posts):
    categories = {}
    for p in posts:
        categories.setdefault(p["category_slug"], []).append(p)

    for cat_slug, cat_posts in categories.items():
        cat_name = cat_posts[0]["category"]
        total = len(cat_posts)
        pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
        for page in range(1, pages + 1):
            start = (page - 1) * PER_PAGE
            end = start + PER_PAGE
            page_posts = cat_posts[start:end]
            path = f"/category/{cat_slug}/"
            if page > 1:
                path = f"/category/{cat_slug}/page/{page}/"
            schema = make_schema("CollectionPage", {
                "name": f"{cat_name} — {SITE_NAME}",
                "url": f"{SITE_URL}{path}",
            })
            render_page(
                "category.html",
                path,
                schema=schema,
                category_name=cat_name,
                posts=page_posts,
                page=page,
                pages=pages,
            )

def generate_post_pages(posts):
    for i, post in enumerate(posts):
        prev_post = posts[i + 1] if i + 1 < len(posts) else None
        next_post = posts[i - 1] if i > 0 else None

        related = [
            p for p in posts
            if p["category_slug"] == post["category_slug"]
            and p["url"] != post["url"]
        ][:3]

        schema = make_schema("Article", {
            "headline": post["title"],
            "description": post["excerpt"],
            "datePublished": post["date_iso"],
            "author": {"@type": "Person", "name": post["author"]},
            "publisher": {"@type": "Organization", "name": SITE_NAME},
            "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE_URL}{post['url']}"},
        })

        article_schema = json.loads(schema)
        if post.get("price_current") is not None:
            article_schema["offers"] = {
                "@type": "Offer",
                "price": post["price_current"],
                "priceCurrency": post.get("price_currency", "EUR"),
                "url": post["affiliate_link"],
                "availability": "https://schema.org/InStock",
            }

        render_page(
            "post.html",
            post["url"],
            schema=json.dumps(article_schema, indent=2, ensure_ascii=False),
            post=post,
            prev_post=prev_post,
            next_post=next_post,
            related_posts=related,
        )

def generate_sitemap(posts):
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    urls = ["/"] + [f"/{p['url']}" for p in posts]
    urls += ["/sobre/", "/privacidade/", "/contacto/"]
    for cat_slug in set(p["category_slug"] for p in posts):
        urls.append(f"/category/{cat_slug}/")

    for url_path in set(urls):
        url_elem = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_elem, "loc")
        loc.text = SITE_URL + url_path
        lastmod = ET.SubElement(url_elem, "lastmod")
        lastmod.text = datetime.date.today().isoformat()
        changefreq = ET.SubElement(url_elem, "changefreq")
        changefreq.text = "weekly" if "/category/" in url_path or url_path == "/" else "monthly"
        priority = ET.SubElement(url_elem, "priority")
        priority.text = "1.0" if url_path == "/" else "0.8"

    tree = ET.ElementTree(urlset)
    tree.write(str(OUTPUT / "sitemap.xml"), encoding="utf-8", xml_declaration=True)

def generate_rss(posts):
    rss_items = ""
    for p in posts[:20]:
        rss_items += f"""
    <item>
      <title>{p['title']}</title>
      <link>{SITE_URL}{p['url']}</link>
      <description>{p['excerpt']}</description>
      <pubDate>{formatdate(datetime.datetime.strptime(p['date_iso'], '%Y-%m-%d').timestamp())}</pubDate>
      <guid>{SITE_URL}{p['url']}</guid>
    </item>"""

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SITE_NAME}</title>
    <link>{SITE_URL}</link>
    <description>{SITE_DESCRIPTION}</description>
    <language>pt-pt</language>
    <lastBuildDate>{formatdate()}</lastBuildDate>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
    {rss_items}
  </channel>
</rss>"""

    (OUTPUT / "rss.xml").write_text(rss, encoding="utf-8")

def generate_robots():
    robots = f"""User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml
"""
    (OUTPUT / "robots.txt").write_text(robots, encoding="utf-8")

def copy_static():
    if STATIC.exists():
        for item in STATIC.iterdir():
            dest = OUTPUT / item.relative_to(STATIC).parent.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(STATIC, OUTPUT, dirs_exist_ok=True)

def generate_site_config():
    config = {
        "site_name": SITE_NAME,
        "site_url": SITE_URL,
        "site_description": SITE_DESCRIPTION,
        "build_date": datetime.date.today().isoformat(),
    }
    (OUTPUT / "site.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

def build():
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    posts = load_all_posts()
    print(f"[POSTS] Loaded {len(posts)} posts")

    copy_static()
    print(f"[STATIC] Copied static assets")

    generate_index(posts)
    print(f"[INDEX] Generated index")

    generate_pages(posts)
    print(f"[PAGES] Generated static pages")

    generate_post_pages(posts)
    print(f"[POSTS] Generated {len(posts)} post pages")

    generate_category_pages(posts)
    print(f"[CATEGORY] Generated category pages")

    generate_sitemap(posts)
    print(f"[SITEMAP] Generated sitemap.xml")

    generate_rss(posts)
    print(f"[RSS] Generated RSS feed")

    generate_robots()
    print(f"[ROBOTS] Generated robots.txt")

    generate_site_config()
    print(f"[CONFIG] Generated site config")

    print(f"\n[DONE] Build complete! Output: {OUTPUT}")

if __name__ == "__main__":
    build()
