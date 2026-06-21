"""Static Site Generator for Casa Inteligente — multi-language."""
import os, re, json, shutil, datetime, xml.etree.ElementTree as ET, copy
from pathlib import Path
from email.utils import formatdate
import yaml, markdown as md_lib
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUTPUT = ROOT / "output"
TEMPLATES = SRC / "templates"
CONTENT = SRC / "content"
STATIC = SRC / "static"
DATA_DIR = ROOT / "data"
PRICES_FILE = DATA_DIR / "prices.json"
I18N_FILE = DATA_DIR / "i18n.json"

LANGUAGES = ["pt", "es", "fr", "en"]
DEFAULT_LANG = "pt"
PER_PAGE = 12

with open(I18N_FILE, "r", encoding="utf-8") as f:
    ALL_I18N = json.load(f)

def load_price_data():
    if PRICES_FILE.exists():
        return json.loads(PRICES_FILE.read_text(encoding="utf-8"))
    return {"products": {}, "last_updated": None}

def extract_asin(url):
    match = re.search(r'/dp/([A-Z0-9]{10})', url)
    return match.group(1) if match else None

def find_product_for_post(post, price_data):
    asin = extract_asin(post.get("affiliate_link", ""))
    if not asin: return None
    for pid, info in price_data.get("products", {}).items():
        if info.get("asin") == asin: return pid
    return None

CATEGORY_MAP = {
    "Guias": "guides", "Reviews": "reviews", "Comparações": "comparacoes",
    "Guías": "guides", "Comparaciones": "comparaciones",
    "Guides": "guides", "Avis": "avis", "Comparaisons": "comparaisons",
    "Comparisons": "comparisons",
}

def get_category_slug(category):
    return CATEGORY_MAP.get(category, category.lower().replace(" ", "-"))

def parse_frontmatter(filepath):
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match: return {"meta": {}, "body": content}
    return {"meta": yaml.safe_load(match.group(1)) or {}, "body": match.group(2).strip()}

def md_to_html(text):
    return md_lib.markdown(text, extensions=["extra", "codehilite", "toc", "sane_lists"])

def read_time(text, wpm=200):
    return max(1, round(len(text.split()) / wpm))

class SiteBuilder:
    def __init__(self, lang):
        self.lang = lang
        self.i18n = ALL_I18N.get(lang, ALL_I18N[DEFAULT_LANG])
        self.site_url = f"https://cliffana.github.io/casainteligente"
        if lang != DEFAULT_LANG:
            self.site_url += f"/{lang}"
        self.site_name = self.i18n["site_name"]
        self.site_description = self.i18n["site_description"]
        self.site_author = self.i18n["site_author"]
        self.site_email = self.i18n["site_email"]
        self.price_data = load_price_data()
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)
        self.env.globals["t"] = self.t
        self.env.globals["lang"] = lang
        self.env.globals["langs"] = [
            {"code": c, "name": ALL_I18N[c][f"language_{c}"]}
            for c in LANGUAGES
        ]
        self.env.globals["current_lang"] = lang
        self.env.globals["default_lang"] = DEFAULT_LANG
        self.env.globals["url_for_lang"] = self.url_for_lang
        self.env.globals["site_url"] = self.site_url
        self.env.globals["site_name"] = self.site_name
        self.env.globals["site_description"] = self.site_description
        self.env.globals["build_year"] = datetime.date.today().year
        self.lang_prefix = "" if lang == DEFAULT_LANG else f"/{lang}"

    def t(self, key, **kwargs):
        val = self.i18n.get(key, key)
        if kwargs:
            return val % kwargs
        return val

    def url_for_lang(self, target_lang, path=""):
        if target_lang == DEFAULT_LANG:
            base = "https://cliffana.github.io/casainteligente"
        else:
            base = f"https://cliffana.github.io/casainteligente/{target_lang}"
        return base + path

    def make_schema(self, schema_type, extra=None):
        schema = {"@context": "https://schema.org", "@type": schema_type, "name": self.site_name, "url": self.site_url, "description": self.site_description}
        if extra: schema.update(extra)
        return json.dumps(schema, indent=4, ensure_ascii=False)

    def render_page(self, template_name, output_path, schema=None, **context):
        template = self.env.get_template(template_name)
        if schema is None:
            schema = self.make_schema("WebSite")
        html = template.render(page_schema=schema, page_url=output_path, **context)
        full_path = OUTPUT / self.lang_prefix.lstrip("/") / output_path.lstrip("/")
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if full_path.suffix == "":
            full_path = full_path / "index.html"
            full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(html, encoding="utf-8")
        return full_path

    def load_posts(self):
        posts = []
        content_dir = CONTENT / self.lang
        if not content_dir.exists():
            return posts
        for ext in ["md", "mdx"]:
            for filepath in sorted(content_dir.rglob(f"*.{ext}")):
                parsed = parse_frontmatter(filepath)
                meta = parsed["meta"]
                html_body = md_to_html(parsed["body"])
                category = meta.get("category", "Geral")
                category_slug = get_category_slug(category)
                slug = filepath.stem
                url = f"/{category_slug}/{slug}/"
                if self.lang != DEFAULT_LANG:
                    url = f"/{self.lang}{url}"
                date = meta.get("date", datetime.date.today())
                if isinstance(date, (datetime.date, datetime.datetime)):
                    date_str = date.strftime("%d/%m/%Y")
                    date_iso = date.isoformat() if isinstance(date, datetime.date) else date.date().isoformat()
                else:
                    try:
                        d = datetime.date.fromisoformat(str(date)[:10])
                        date_str = d.strftime("%d/%m/%Y")
                        date_iso = d.isoformat()
                    except (ValueError, TypeError):
                        date_str = str(date); date_iso = str(date)
                affiliate_link = meta.get("affiliate_link", "")
                product_id = find_product_for_post(meta, self.price_data)
                post = {
                    "title": meta.get("title", filepath.stem.replace("-", " ").title()),
                    "excerpt": meta.get("excerpt", ""),
                    "content": html_body,
                    "date": date_str,
                    "date_iso": date_iso,
                    "updated": meta.get("updated", ""),
                    "author": meta.get("author", self.site_author),
                    "category": category,
                    "category_slug": category_slug,
                    "url": url,
                    "image": meta.get("image", "default.jpg"),
                    "rating": meta.get("rating"),
                    "read_time": read_time(parsed["body"]),
                    "featured": meta.get("featured", False),
                    "affiliate_link": affiliate_link,
                    "affiliate_disclosure": meta.get("affiliate_disclosure", self.t("affiliate_disclosure")),
                    "cta_text": meta.get("cta_text", ""),
                    "tags": meta.get("tags", []),
                    "product_id": product_id,
                    "faq": meta.get("faq", []),
                    "filepath": filepath,
                }
                if product_id and product_id in self.price_data.get("products", {}):
                    pinfo = self.price_data["products"][product_id]
                    post["price_history"] = pinfo.get("history", [])
                    post["price_currency"] = pinfo.get("currency", "EUR")
                    post["price_current"] = post["price_history"][-1]["price"] if post["price_history"] else None
                    post["price_min"] = min(p["price"] for p in post["price_history"]) if post["price_history"] else None
                    post["price_max"] = max(p["price"] for p in post["price_history"]) if post["price_history"] else None
                posts.append(post)
        posts.sort(key=lambda p: p["date_iso"], reverse=True)
        return posts

    def generate_index(self, posts):
        featured = next((p for p in posts if p["featured"]), None)
        guides = [p for p in posts if p["category_slug"] == "guides"][:6]
        reviews = [p for p in posts if p["category_slug"] == "reviews"][:6]
        comparisons = [p for p in posts if p["category_slug"] in ("comparacoes", "comparaciones", "comparaisons", "comparisons")][:6]
        schema = self.make_schema("WebSite", {
            "url": self.site_url,
            "potentialAction": {"@type": "SearchAction", "target": self.site_url + "/?s={search_term}", "query-input": "required name=search_term"}
        })
        self.render_page("index.html", "/", schema=schema, featured_post=featured, guides=guides, reviews=reviews, comparisons=comparisons)

    def generate_pages(self, posts):
        pages = [
            ("sobre", "about.html", self.t("about_title")),
            ("privacidade", "privacy.html", self.t("privacy_title")),
            ("contacto", "contact.html", self.t("contact_title")),
        ]
        for slug, template, title in pages:
            schema = self.make_schema("WebPage", {"name": title, "url": f"{self.site_url}/{slug}/"})
            self.render_page(template, f"/{slug}/", schema=schema)

    def generate_category_pages(self, posts):
        categories = {}
        for p in posts:
            categories.setdefault(p["category_slug"], []).append(p)
        for cat_slug, cat_posts in categories.items():
            cat_name = cat_posts[0]["category"]
            total = len(cat_posts)
            pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
            for page in range(1, pages + 1):
                start = (page - 1) * PER_PAGE; end = start + PER_PAGE
                page_posts = cat_posts[start:end]
                path = f"/category/{cat_slug}/"
                if page > 1: path = f"/category/{cat_slug}/page/{page}/"
                schema = self.make_schema("CollectionPage", {"name": f"{cat_name} — {self.site_name}", "url": f"{self.site_url}{path}"})
                self.render_page("category.html", path, schema=schema, category_name=cat_name, posts=page_posts, page=page, pages=pages)

    def generate_post_pages(self, posts):
        for i, post in enumerate(posts):
            prev_post = posts[i + 1] if i + 1 < len(posts) else None
            next_post = posts[i - 1] if i > 0 else None
            related = [p for p in posts if p["category_slug"] == post["category_slug"] and p["url"] != post["url"]][:3]
            article_schema = {"@type": "Article", "headline": post["title"], "description": post["excerpt"],
                "datePublished": post["date_iso"], "author": {"@type": "Person", "name": post["author"]},
                "publisher": {"@type": "Organization", "name": self.site_name},
                "mainEntityOfPage": {"@type": "WebPage", "@id": f"{self.site_url}{post['url']}"}}
            if post.get("price_current") is not None:
                article_schema["offers"] = {"@type": "Offer", "price": post["price_current"],
                    "priceCurrency": post.get("price_currency", "EUR"), "url": post["affiliate_link"],
                    "availability": "https://schema.org/InStock"}
            schema = self.make_schema("Article", article_schema)
            self.render_page("post.html", post["url"], schema=schema, post=post, prev_post=prev_post, next_post=next_post, related_posts=related)

    def generate_sitemap(self, posts):
        urlset = ET.Element("urlset"); urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        urls = ["/"] + [p["url"] for p in posts]
        for slug in ("sobre", "privacidade", "contacto"):
            urls.append(f"/{slug}/")
        for cat_slug in set(p["category_slug"] for p in posts):
            urls.append(f"/category/{cat_slug}/")
        for url_path in set(urls):
            u = ET.SubElement(urlset, "url")
            ET.SubElement(u, "loc").text = self.site_url + url_path
            ET.SubElement(u, "lastmod").text = datetime.date.today().isoformat()
            cf = "weekly" if "/category/" in url_path or url_path == "/" else "monthly"
            ET.SubElement(u, "changefreq").text = cf
            p = ET.SubElement(u, "priority")
            p.text = "1.0" if url_path == "/" else "0.8"
        out_dir = OUTPUT / self.lang_prefix.lstrip("/")
        out_dir.mkdir(parents=True, exist_ok=True)
        ET.ElementTree(urlset).write(str(out_dir / "sitemap.xml"), encoding="utf-8", xml_declaration=True)

    def generate_rss(self, posts):
        items = ""
        for p in posts[:20]:
            ts = datetime.datetime.strptime(p['date_iso'], '%Y-%m-%d').timestamp()
            items += f"""\n    <item>\n      <title>{p['title']}</title>\n      <link>{self.site_url}{p['url']}</link>\n      <description>{p['excerpt']}</description>\n      <pubDate>{formatdate(ts)}</pubDate>\n      <guid>{self.site_url}{p['url']}</guid>\n    </item>"""
        rss = f"""<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n  <channel>\n    <title>{self.site_name}</title>\n    <link>{self.site_url}</link>\n    <description>{self.site_description}</description>\n    <language>{self.lang}-{self.lang.upper()}</language>\n    <lastBuildDate>{formatdate()}</lastBuildDate>\n    <atom:link href="{self.site_url}/rss.xml" rel="self" type="application/rss+xml"/>{items}\n  </channel>\n</rss>"""
        out_dir = OUTPUT / self.lang_prefix.lstrip("/")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "rss.xml").write_text(rss, encoding="utf-8")

    def generate_robots(self):
        robots = f"User-agent: *\nAllow: /\nSitemap: {self.site_url}/sitemap.xml\n"
        out_dir = OUTPUT / self.lang_prefix.lstrip("/")
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "robots.txt").write_text(robots, encoding="utf-8")

    def build(self):
        posts = self.load_posts()
        print(f"[{self.lang.upper()}] Loaded {len(posts)} posts")
        self.generate_index(posts)
        print(f"[{self.lang.upper()}] Index generated")
        self.generate_pages(posts)
        print(f"[{self.lang.upper()}] Static pages generated")
        self.generate_post_pages(posts)
        print(f"[{self.lang.upper()}] {len(posts)} post pages generated")
        self.generate_category_pages(posts)
        print(f"[{self.lang.upper()}] Category pages generated")
        self.generate_sitemap(posts)
        print(f"[{self.lang.upper()}] Sitemap generated")
        self.generate_rss(posts)
        print(f"[{self.lang.upper()}] RSS generated")
        self.generate_robots()
        print(f"[{self.lang.upper()}] Robots.txt generated")

def build():
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)

    static_dest = OUTPUT / "css"
    static_dest.mkdir(parents=True, exist_ok=True)
    if (STATIC / "css" / "style.css").exists():
        shutil.copy2(STATIC / "css" / "style.css", OUTPUT / "css" / "style.css")
    if (STATIC / "js" / "main.js").exists():
        js_dest = OUTPUT / "js"
        js_dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(STATIC / "js" / "main.js", OUTPUT / "js" / "main.js")

    for lang in LANGUAGES:
        print(f"\n{'='*40}\nBuilding: {lang.upper()}\n{'='*40}")
        builder = SiteBuilder(lang)
        builder.build()

    index_src = OUTPUT / "index.html"
    if not index_src.exists() and (OUTPUT / "pt" / "index.html").exists():
        shutil.copy2(OUTPUT / "pt" / "index.html", index_src)
        shutil.copy2(OUTPUT / "pt" / "sitemap.xml", OUTPUT / "sitemap.xml")
        shutil.copy2(OUTPUT / "pt" / "rss.xml", OUTPUT / "rss.xml")
        shutil.copy2(OUTPUT / "pt" / "robots.txt", OUTPUT / "robots.txt")
        for f in ["sobre", "privacidade", "contacto", "category"]:
            src_dir = OUTPUT / "pt" / f
            if src_dir.exists():
                dst_dir = OUTPUT / f
                if dst_dir.exists(): shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)

    print(f"\n{'='*40}\n[DONE] Build complete! Output: {OUTPUT}\n{'='*40}")

if __name__ == "__main__":
    build()
