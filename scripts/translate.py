"""Translate PT content to ES, FR, EN using Claude API."""
import os, re, json, datetime
from pathlib import Path

import yaml
from anthropic import Anthropic

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "src" / "content"
I18N_FILE = ROOT / "data" / "i18n.json"

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"

LANGUAGES = {
    "es": {"name": "Español (España)", "code": "es-ES"},
    "fr": {"name": "Français (France)", "code": "fr-FR"},
    "en": {"name": "English (US)", "code": "en-US"},
}

def load_i18n():
    data = json.loads(I18N_FILE.read_text(encoding="utf-8"))
    return data

def load_all_pt_posts():
    posts = []
    pt_dir = CONTENT_DIR / "pt"
    if not pt_dir.exists():
        return posts
    for ext in ["md", "mdx"]:
        for filepath in sorted(pt_dir.rglob(f"*.{ext}")):
            content = filepath.read_text(encoding="utf-8")
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
            if not match:
                continue
            meta = yaml.safe_load(match.group(1)) or {}
            body = match.group(2).strip()
            posts.append({"filepath": filepath, "meta": meta, "body": body, "slug": filepath.stem})
    return posts

def translate_with_claude(text, target_lang, lang_info, context_title=""):
    if not API_KEY:
        print(f"  [WARN] ANTHROPIC_API_KEY not set. Using original text.")
        return text

    client = Anthropic(api_key=API_KEY)
    prompt = f"""Translate the following article from Portuguese (Portugal) to {lang_info['name']} ({lang_info['code']}).

Requirements:
- Translate naturally for {lang_info['name']} readers
- Keep ALL Markdown formatting, headings, tables, lists, and links intact
- Do NOT change any URLs or affiliate links
- Do NOT change the ASIN codes or product IDs
- Keep the price format in EUR (€)
- Adapt measurements and cultural references where appropriate
- The tone should be informative, trustworthy, and slightly conversational
- Output ONLY the translated Markdown body, no additional text

Title: {context_title}

Article body:
{text}"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

def translate_frontmatter(meta, target_lang, i18n_data):
    new_meta = dict(meta)
    lang_i18n = i18n_data.get(target_lang, {})

    title = meta.get("title", "")
    excerpt = meta.get("excerpt", "")
    tags = meta.get("tags", [])
    category = meta.get("category", "")

    category_map = {
        "Guias": {"es": "Guías", "fr": "Guides", "en": "Guides"},
        "Reviews": {"es": "Reviews", "fr": "Avis", "en": "Reviews"},
        "Comparações": {"es": "Comparaciones", "fr": "Comparaisons", "en": "Comparisons"},
    }
    if category in category_map and target_lang in category_map[category]:
        new_meta["category"] = category_map[category][target_lang]

    author_map = {
        "es": "Equipo Casa Inteligente ES",
        "fr": "Équipe Casa Inteligente FR",
        "en": "Casa Inteligente Team",
    }
    new_meta["author"] = author_map.get(target_lang, meta.get("author", ""))

    disclosure_map = {
        "es": "Este artículo contiene enlaces de afiliados. Podremos recibir una comisión por compras realizadas a través de estos enlaces, sin coste adicional para usted.",
        "fr": "Cet article contient des liens d'affiliation. Nous pouvons recevoir une commission pour les achats effectués via ces liens, sans frais supplémentaires pour vous.",
        "en": "This article contains affiliate links. We may receive a commission for purchases made through these links, at no extra cost to you.",
    }
    new_meta["affiliate_disclosure"] = disclosure_map.get(target_lang, meta.get("affiliate_disclosure", ""))

    faq = meta.get("faq", [])
    new_meta["faq"] = faq

    return new_meta

def translate_faq(faq_list, target_lang, lang_info, context_title=""):
    if not faq_list or not API_KEY:
        return faq_list

    try:
        client = Anthropic(api_key=API_KEY)
        faq_text = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in faq_list])
        prompt = f"""Translate these FAQ items from Portuguese to {lang_info['name']} ({lang_info['code']}).

Requirements:
- Natural, native translation
- Keep Q: and A: format exactly
- Output ONLY the translated FAQ, no additional text

Article: {context_title}

{faq_text}"""

        message = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        result = message.content[0].text
        translated = []
        for line in result.strip().split("\n"):
            q_match = re.match(r"^Q:\s*(.*)", line)
            a_match = re.match(r"^A:\s*(.*)", line)
            if q_match and translated:
                pass
            elif q_match:
                translated.append({"question": q_match.group(1).strip(), "answer": ""})
            elif a_match and translated:
                translated[-1]["answer"] = a_match.group(1).strip()
        return translated if translated else faq_list
    except Exception as e:
        print(f"  [ERR FAQ] {e}")
        return faq_list

def translate_all():
    i18n_data = load_i18n()
    posts = load_all_pt_posts()
    print(f"[TRANSLATE] Found {len(posts)} PT articles to translate\n")

    for post in posts:
        slug = post["slug"]
        body = post["body"]
        meta = post["meta"]
        title = meta.get("title", slug)

        for target_lang, lang_info in LANGUAGES.items():
            target_dir = CONTENT_DIR / target_lang
            target_file = target_dir / f"{slug}.md"
            category_slug = meta.get("category", "").lower()
            category_dir_map = {"guias": "guides", "reviews": "reviews", "comparações": "comparacoes"}
            target_subdir = target_dir / category_dir_map.get(category_slug, "guides")
            target_subdir.mkdir(parents=True, exist_ok=True)
            target_file = target_subdir / f"{slug}.md"

            if target_file.exists():
                print(f"  [SKIP] {slug} → {target_lang.upper()} (already exists)")
                continue

            print(f"  [>>] {slug} → {target_lang.upper()}")

            new_meta = translate_frontmatter(meta, target_lang, i18n_data)

            translated_body = translate_with_claude(body, target_lang, lang_info, title)

            if meta.get("faq"):
                new_meta["faq"] = translate_faq(meta["faq"], target_lang, lang_info, title)

            yaml_front = yaml.dump(new_meta, allow_unicode=True, default_flow_style=False, sort_keys=False)
            content = f"---\n{yaml_front}---\n\n{translated_body.strip()}\n"
            target_subdir.mkdir(parents=True, exist_ok=True)
            target_file = target_subdir / f"{slug}.md"
            target_file.write_text(content, encoding="utf-8")
            print(f"  [OK]  Saved: {target_file.relative_to(ROOT)}")

    print(f"\n[DONE] Translation complete!")

if __name__ == "__main__":
    translate_all()
