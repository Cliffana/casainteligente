"""AI Content Generation Pipeline for affiliate articles.

This script generates SEO-optimized markdown content files
using the Claude API (or other LLM providers).
"""

import os
import re
import json
import datetime
import argparse
from pathlib import Path

import yaml
from anthropic import Anthropic

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "src" / "content"

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"

TRACKING_ID = "casainteli0e7-21"
AMAZON_TAG = f"?tag={TRACKING_ID}"

CONTENT_BRIEFS = [
    {
        "id": "guia-iniciante-casa-inteligente",
        "title": "Guia Completo de Casa Inteligente para Iniciantes 2026",
        "category": "Guias",
        "excerpt": "Tudo o que precisa para começar a automatizar a sua casa. Dos dispositivos essenciais à configuração passo a passo.",
        "keywords": ["casa inteligente", "automação residencial", "iniciante", "smart home Portugal", "guia completo"],
        "product_id": "echo-dot-5",
        "outline": [
            "O que é uma casa inteligente?",
            "Por onde começar? (orçamento, prioridades)",
            "Dispositivos essenciais para iniciantes",
            "Amazon Alexa vs Google Home vs Apple HomeKit",
            "Protocolos: WiFi, Zigbee, Z-Wave, Matter",
            "Passo a passo: configurar o primeiro dispositivo",
            "Automações simples para começar",
            "Orçamento: casa inteligente por menos de 200€",
            "Erros comuns de principiantes",
            "Próximos passos após o setup inicial",
        ],
        "cta_text": "Pronto para começar? Veja os melhores kits de casa inteligente para iniciantes.",
        "affiliate_link": f"https://www.amazon.es/dp/B09B8X9RGM{AMAZON_TAG}",
        "faq": [
            {"question": "Quanto custa começar uma casa inteligente?", "answer": "Pode começar por menos de 50€ com um Amazon Echo Dot e uma tomada inteligente. Um setup completo fica entre 200€ e 500€."},
            {"question": "Preciso de internet para casa inteligente?", "answer": "Sim, a maioria dos dispositivos requer WiFi. Alguns usam Zigbee ou Bluetooth mas precisam de um hub ligado à internet."},
            {"question": "Vale a pena investir em casa inteligente?", "answer": "Sim, especialmente para segurança, poupança de energia e conveniência no dia a dia."},
        ],
        "featured": True,
    },
    {
        "id": "melhores-colunas-inteligentes-2026",
        "title": "Melhores Colunas Inteligentes 2026: Alexa vs Google Nest vs HomePod",
        "category": "Reviews",
        "excerpt": "Comparámos as melhores colunas inteligentes do mercado. Qual a melhor para si? Descubra neste review completo.",
        "keywords": ["coluna inteligente", "Amazon Echo", "Google Nest", "HomePod", "melhor smart speaker"],
        "product_id": "echo-dot-5",
        "outline": [
            "Introdução: qual a melhor coluna inteligente?",
            "Amazon Echo Dot (5ª geração)",
            "Amazon Echo Studio",
            "Google Nest Audio",
            "Google Nest Hub (ecrã incluído)",
            "Apple HomePod Mini",
            "Tabela comparativa: preço, som, funcionalidades",
            "Qual escolher conforme o seu ecossistema",
            "Veredito final",
        ],
        "cta_text": "Veja o preço mais recente do Amazon Echo Dot — a melhor escolha para iniciantes.",
        "affiliate_link": f"https://www.amazon.es/dp/B09B8X9RGM{AMAZON_TAG}",
        "faq": [
            {"question": "Qual a melhor coluna inteligente para iniciantes?", "answer": "O Amazon Echo Dot 5ª geração é a melhor opção pela relação qualidade-preço, com bom som e acesso a milhares de skills."},
            {"question": "Google Nest ou Amazon Echo: qual escolher?", "answer": "Escolha Google Nest se usa serviços Google, Amazon Echo se usa Prime e Alexa. Ambos são excelentes."},
            {"question": "Vale a pena comprar uma coluna com ecrã?", "answer": "Sim, para videochamadas, receitas e controlo visual da casa inteligente. O Nest Hub é a melhor opção."},
        ],
        "featured": False,
    },
    {
        "id": "comparacao-xiaomi-vs-tuya",
        "title": "Xiaomi vs Tuya: Qual o Melhor Ecossistema para Casa Inteligente?",
        "category": "Comparações",
        "excerpt": "Xiaomi Aqara ou Tuya? Comparamos preço, compatibilidade, qualidade e facilidade de uso dos dois ecossistemas.",
        "keywords": ["Xiaomi vs Tuya", "Aqara vs Tuya", "ecossistema casa inteligente", "comparação smart home"],
        "product_id": "tapo-p115",
        "outline": [
            "Introdução: dois gigantes da casa inteligente",
            "Xiaomi/Aqara: vantagens e desvantagens",
            "Tuya/Smart Life: vantagens e desvantagens",
            "Comparação de sensores (porta, movimento, temperatura)",
            "Comparação de lâmpadas e interruptores",
            "Comparação de câmaras de segurança",
            "Compatibilidade com Alexa, Google e HomeKit",
            "Home Assistant: qual funciona melhor?",
            "Preço vs qualidade: análise custo-benefício",
            "Qual escolher em 2026?",
        ],
        "cta_text": "Veja os melhores sensores Xiaomi com os melhores preços.",
        "affiliate_link": f"https://www.amazon.es/dp/B0H2V9Q87H{AMAZON_TAG}",
        "faq": [
            {"question": "Xiaomi ou Tuya: qual é mais barato?", "answer": "A Xiaomi Aqara tende a ser ligeiramente mais cara mas com melhor qualidade de construção. A Tuya oferece mais opções de baixo custo."},
            {"question": "Qual funciona melhor com Home Assistant?", "answer": "Ambos funcionam bem, mas a Xiaomi Aqara via gateway Zigbee tem integração mais estável com Home Assistant."},
            {"question": "Posso misturar dispositivos Xiaomi e Tuya?", "answer": "Sim, desde que ambos suportem o mesmo assistente (Alexa, Google Home). Para automações locais, precisa de um hub compatível."},
        ],
        "featured": False,
    },
]

SYSTEM_PROMPT = """You are a professional content writer for a Portuguese affiliate website about smart home technology (Casa Inteligente PT).

Write in European Portuguese (pt-PT), not Brazilian Portuguese.

Requirements:
- Write naturally, as a human expert. Avoid AI-sounding phrases.
- Be specific, factual, and helpful. Include real product names, exact prices in EUR, and honest pros/cons.
- STRUCTURE IS KEY: Use short paragraphs (2-3 sentences max). Readers scan, they don't read.
- Include at least ONE comparison table with product/specs/price columns.
- Use bullet points for lists of features or options.
- For reviews, include a pros/cons section with a markdown table or lists.
- Include a "Key Takeaways" or "TL;DR" section near the top (after intro) with 3-5 bullet points.
- End with a clear "Veredito" (verdict) section summarizing the recommendation.
- Write for Portuguese readers — mention Amazon PT prices where relevant.
- The tone should be informative, trustworthy, and slightly conversational.
- Output in valid Markdown format (no YAML frontmatter — I will add that separately).
- Use ## for section headings.
- Include the affiliate link naturally within the content (e.g., "pode encontrar [aqui](LINK)").
- Write 1200-2000 words — be concise, every sentence must add value. No fluff.
- NEVER use generic filler phrases like "no mundo digital de hoje" or "vamos mergulhar"."""

def call_llm(prompt, max_tokens=4000):
    if not API_KEY:
        print("[WARN] ANTHROPIC_API_KEY not set. Generate a draft instead.")
        return generate_draft(prompt)

    client = Anthropic(api_key=API_KEY)
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text

def generate_draft(prompt):
    from template_content import generate_all as gen_templates
    try:
        gen_templates()
    except Exception as e:
        print(f"  [WARN] Template fallback failed: {e}")
    return None

def build_prompt(brief):
    outline_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(brief["outline"]))
    prompt = f"""Write a comprehensive article in European Portuguese (pt-PT) for a smart home affiliate website.

Title: {brief['title']}
Excerpt: {brief['excerpt']}
Target Keywords: {', '.join(brief['keywords'])}

Outline:
{outline_text}

{"" + brief['cta_text'] + " - " + brief['affiliate_link'] if brief.get('cta_text') else ""}

{SYSTEM_PROMPT}

Remember: write in European Portuguese (pt-PT), be specific and helpful, 1500-2500 words."""
    return prompt

def save_article(brief, body):
    slug = brief["id"]
    category_slug = brief["category"].lower()
    category_dir = {
        "guias": "guides",
        "reviews": "reviews",
        "comparações": "comparacoes",
    }.get(category_slug, "guides")

    target_dir = CONTENT_DIR / category_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today()
    tags_str = ", ".join(brief["keywords"])
    disclosure = "Este artigo contém links de afiliados. Poderemos receber uma comissão por compras efetuadas através destes links, sem custo adicional para si."

    frontmatter = {
        "title": brief["title"],
        "date": today.isoformat(),
        "category": brief["category"],
        "excerpt": brief["excerpt"],
        "author": "Equipa Casa Inteligente PT",
        "tags": brief["keywords"],
        "featured": brief.get("featured", False),
        "affiliate_link": brief.get("affiliate_link", ""),
        "affiliate_disclosure": disclosure,
        "cta_text": brief.get("cta_text", ""),
        "product_id": brief.get("product_id", ""),
        "faq": brief.get("faq", []),
    }

    yaml_front = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = f"---\n{yaml_front}---\n\n{body.strip()}\n"

    filepath = target_dir / f"{slug}.md"
    filepath.write_text(content, encoding="utf-8")
    print(f"  [SAVED] {filepath.relative_to(ROOT)}")
    return filepath

def generate_all():
    if not API_KEY:
        print("[AI] No API key. Using template-based content instead.")
        from template_content import generate_all as gen_templates
        gen_templates()
        return

    print(f"[AI] Generating {len(CONTENT_BRIEFS)} articles...\n")
    for brief in CONTENT_BRIEFS:
        print(f"  [>>] {brief['title']}")
        prompt = build_prompt(brief)
        try:
            body = call_llm(prompt)
            save_article(brief, body)
        except Exception as e:
            print(f"  [ERR] {e}")
            print("  [FALLBACK] Using template content")
            from template_content import generate_all as gen_templates
            gen_templates()
    print(f"\n[DONE] Generation complete! Files saved to {CONTENT_DIR}")

def generate_single(brief_id):
    brief = next((b for b in CONTENT_BRIEFS if b["id"] == brief_id), None)
    if not brief:
        print(f"[ERR] Brief '{brief_id}' not found")
        return
    print(f"  [>>] {brief['title']}")
    prompt = build_prompt(brief)
    body = call_llm(prompt)
    save_article(brief, body)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Content Generator")
    parser.add_argument("--id", help="Generate a single article by ID")
    parser.add_argument("--list", action="store_true", help="List available briefs")
    args = parser.parse_args()

    if args.list:
        print("Available content briefs:")
        for b in CONTENT_BRIEFS:
            print(f"  - {b['id']}: {b['title']}")
    elif args.id:
        generate_single(args.id)
    else:
        generate_all()
