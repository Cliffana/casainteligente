"""Generate realistic template-based content as fallback when API key is not available.

This produces professional-looking articles with proper structure, tables,
pros/cons, FAQs, and affiliate links. CI will replace these with AI content.
"""

import datetime
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "src" / "content"
TRACKING_ID = "casainteli0e7-21"
AMAZON_TAG = f"?tag={TRACKING_ID}"

ARTICLES = [
    {
        "id": "guia-iniciante-casa-inteligente",
        "lang": "pt",
        "category": "Guias",
        "subdir": "guides",
        "title": "Guia Completo de Casa Inteligente para Iniciantes 2026",
        "excerpt": "Tudo o que precisa para começar a automatizar a sua casa. Dos dispositivos essenciais à configuração passo a passo.",
        "tags": ["casa inteligente", "automação residencial", "iniciante", "smarthome Portugal", "guia completo"],
        "featured": True,
        "affiliate_link": f"https://www.amazon.es/dp/B09B8X9RGM{AMAZON_TAG}",
        "product_id": "echo-dot-5",
        "cta_text": "Pronto para começar? Veja os melhores kits de casa inteligente para iniciantes.",
        "faq": [
            {"question": "Quanto custa começar uma casa inteligente?", "answer": "Pode começar por menos de 50€ com um Amazon Echo Dot e uma tomada inteligente. Um setup completo fica entre 200€ e 500€."},
            {"question": "Preciso de internet para casa inteligente?", "answer": "Sim, a maioria dos dispositivos requer WiFi. Alguns usam Zigbee ou Bluetooth mas precisam de um hub ligado à internet."},
            {"question": "Vale a pena investir em casa inteligente?", "answer": "Sim, especialmente para segurança, poupança de energia e conveniência no dia a dia."},
        ],
    },
    {
        "id": "melhores-colunas-inteligentes-2026",
        "lang": "pt",
        "category": "Reviews",
        "subdir": "reviews",
        "title": "Melhores Colunas Inteligentes 2026: Alexa vs Google Nest vs HomePod",
        "excerpt": "Comparámos as melhores colunas inteligentes do mercado. Qual a melhor para si? Descubra neste review completo.",
        "tags": ["coluna inteligente", "Amazon Echo", "Google Nest", "HomePod", "melhor smart speaker"],
        "featured": False,
        "affiliate_link": f"https://www.amazon.es/dp/B09B8X9RGM{AMAZON_TAG}",
        "product_id": "echo-dot-5",
        "cta_text": "Veja o preço mais recente do Amazon Echo Dot — a melhor escolha para iniciantes.",
        "faq": [
            {"question": "Qual a melhor coluna inteligente para iniciantes?", "answer": "O Amazon Echo Dot 5ª geração é a melhor opção pela relação qualidade-preço, com bom som e acesso a milhares de skills."},
            {"question": "Google Nest ou Amazon Echo: qual escolher?", "answer": "Escolha Google Nest se usa serviços Google, Amazon Echo se usa Prime e Alexa. Ambos são excelentes."},
            {"question": "Vale a pena comprar uma coluna com ecrã?", "answer": "Sim, para videochamadas, receitas e controlo visual da casa inteligente. O Nest Hub é a melhor opção."},
        ],
    },
    {
        "id": "comparacao-xiaomi-vs-tuya",
        "lang": "pt",
        "category": "Comparações",
        "subdir": "comparacoes",
        "title": "Xiaomi vs Tuya: Qual o Melhor Ecossistema para Casa Inteligente?",
        "excerpt": "Xiaomi Aqara ou Tuya? Comparamos preço, compatibilidade, qualidade e facilidade de uso dos dois ecossistemas.",
        "tags": ["Xiaomi vs Tuya", "Aqara vs Tuya", "ecossistema casa inteligente", "comparação smart home"],
        "featured": False,
        "affiliate_link": f"https://www.amazon.es/dp/B0H2V9Q87H{AMAZON_TAG}",
        "product_id": "tapo-p115",
        "cta_text": "Veja os melhores sensores Xiaomi com os melhores preços.",
        "faq": [
            {"question": "Xiaomi ou Tuya: qual é mais barato?", "answer": "A Xiaomi Aqara tende a ser ligeiramente mais cara mas com melhor qualidade de construção. A Tuya oferece mais opções de baixo custo."},
            {"question": "Qual funciona melhor com Home Assistant?", "answer": "Ambos funcionam bem, mas a Xiaomi Aqara via gateway Zigbee tem integração mais estável com Home Assistant."},
            {"question": "Posso misturar dispositivos Xiaomi e Tuya?", "answer": "Sim, desde que ambos suportem o mesmo assistente (Alexa, Google Home). Para automações locais, precisa de um hub compatível."},
        ],
    },
]

def get_pt_article_body(title):
    if "iniciante" in title.lower():
        return """## TL;DR — Principais Conclusões

- Pode montar uma casa inteligente por menos de 50€ com um Amazon Echo Dot e uma tomada WiFi
- O ecossistema Matter está a unificar todos os protocolos — escolha dispositivos compatíveis
- Comece por um aspeto (iluminação ou tomadas) e expanda gradualmente
- A segurança deve ser prioridade: rede separada para IoT e atualizações regulares
- Home Assistant é a plataforma mais versátil para utilizadores avançados

## O que é uma casa inteligente?

Uma casa inteligente (smart home) é uma residência equipada com dispositivos conectados à internet que podem ser controlados remotamente ou automatizados. Desde ligar as luzes com um comando de voz até ajustar o termóstato automaticamente quando sai de casa, a tecnologia smart home torna o seu dia a dia mais prático, eficiente e seguro.

O mercado de casa inteligente em Portugal cresceu mais de 35% em 2025, com cada vez mais portugueses a descobrir as vantagens da automação residencial. E a boa notícia? Nunca foi tão acessível começar.

## Por onde começar? Orçamento e prioridades

Antes de comprar o primeiro dispositivo, responda a três perguntas:

1. **Qual o seu orçamento inicial?** — Recomendamos começar com 50€ a 100€
2. **Qual o assistente virtual que prefere?** — Alexa (Amazon), Google Assistant ou Apple HomeKit
3. **Qual o problema que quer resolver primeiro?** — Iluminação, segurança, poupança de energia?

> **Dica**: Comece pequeno. Um [Amazon Echo Dot](https://www.amazon.es/dp/B09B8X9RGM?tag=casainteli0e7-21) e uma tomada inteligente são suficientes para sentir o impacto da automação no seu dia a dia.

## Dispositivos essenciais para iniciantes

| Dispositivo | Preço médio | Função principal | Recomendado |
|------------|------------|------------------|-------------|
| Coluna inteligente (Echo Dot) | 35-50€ | Comando de voz e hub | Amazon Echo Dot 5ª gen |
| Tomada inteligente | 8-15€ | Controlar dispositivos | TP-Link Tapo P115 |
| Lâmpada inteligente | 10-25€ | Iluminação automatizada | Philips Hue White |
| Sensor de porta/janela | 10-20€ | Segurança e automação | Aqara Door Sensor |
| Hub Zigbee | 30-50€ | Conectar sensores | Aqara Hub M2 |

### Coluna inteligente — o centro do seu ecossistema

A coluna inteligente é o dispositivo mais importante. Serve como assistente de voz, hub de controlo e altifalante para música. O [Amazon Echo Dot 5ª geração](https://www.amazon.es/dp/B09B8X9RGM?tag=casainteli0e7-21) é a nossa recomendação para iniciantes pela excelente relação qualidade-preço.

### Tomadas inteligentes — a porta de entrada

Com uma tomada inteligente, pode transformar qualquer dispositivo "burro" num dispositivo inteligente. Liga e desliga remotamente, cria horários e monitoriza o consumo de energia. A [TP-Link Tapo P115](https://www.amazon.es/dp/B0H2V9Q87H?tag=casainteli0e7-21) é a melhor opção de entrada de gama.

## Amazon Alexa vs Google Home vs Apple HomeKit

| Característica | Amazon Alexa | Google Home | Apple HomeKit |
|---------------|-------------|-------------|---------------|
| Disponibilidade em PT | Excelente | Boa | Limitada |
| Número de dispositivos compatíveis | Superior | Médio | Reduzido |
| Facilidade de configuração | Muito fácil | Fácil | Moderada |
| Preço entrada | 35€ | 60€ | 100€+ |
| Automações avançadas | Sim (Routines) | Sim | Sim |
| Controlo por voz em PT | Sim | Sim | Parcial |

**Veredito**: Para a maioria dos portugueses, a Amazon Alexa é a melhor escolha pela disponibilidade em português, preço acessível e vasta compatibilidade com dispositivos.

## Protocolos: WiFi, Zigbee, Z-Wave e Matter

Compreender os protocolos é essencial para fazer escolhas acertadas:

- **WiFi** — Dispositivos ligam-se diretamente à sua rede. Fácil de configurar, mas consome mais largura de banda.
- **Zigbee** — Rede mesh de baixo consumo. Precisa de um hub, mas é mais fiável para muitos dispositivos.
- **Z-Wave** — Similar ao Zigbee, mas menos comum na Europa.
- **Matter** — O novo padrão universal. Dispositivos Matter funcionam com qualquer assistente.

## Passo a passo: configurar o primeiro dispositivo

1. **Compre o seu Echo Dot** na Amazon.es pelo [melhor preço](https://www.amazon.es/dp/B09B8X9RGM?tag=casainteli0e7-21)
2. **Ligue à corrente** e aguarde o LED laranja
3. **Abra a app Alexa** no seu smartphone e siga as instruções
4. **Ligue à sua rede WiFi** quando a app pedir
5. **Faça o primeiro teste**: "Alexa, que horas são?"
6. **Adicione uma tomada inteligente** e diga "Alexa, descobre dispositivos"
7. **Crie uma rotina**: "Alexa, boa noite" → apagar luzes e trancar portas

## Automações simples para começar

- **Boa noite**: Um comando desliga todas as luzes e tomadas
- **Bom dia**: Acender luzes suavemente e dar a previsão do tempo
- **Ao sair de casa**: Desligar dispositivos e ativar o modo ausente
- **Chegada a casa**: Acender luzes de entrada e desativar alarme

## Orçamento: casa inteligente por menos de 200€

| Item | Preço |
|------|-------|
| Amazon Echo Dot 5ª gen | 35-50€ |
| 2x Tomadas TP-Link Tapo P115 | 20-30€ |
| 2x Lâmpadas Philips Hue White | 20-40€ |
| Sensor Aqara porta/janela | 15-20€ |
| Hub Aqara Zigbee | 30-40€ |
| **Total estimado** | **120-180€** |

## Erros comuns de principiantes

- Comprar muitos dispositivos de uma vez sem testar o ecossistema
- Ignorar a compatibilidade entre marcas
- Não atualizar o firmware dos dispositivos
- Colocar todos os dispositivos na mesma rede sem segmentação
- Esquecer a segurança: usar palavras-passe fortes e 2FA sempre que possível

## Próximos passos

Depois do setup inicial, explore:
- **Sensores de temperatura e humidade** para climatização inteligente
- **Câmaras de segurança** para monitorização remota
- **Cortinas motorizadas** para automação total
- **Home Assistant** para controlo avançado e local

> Pronto para começar a sua jornada smart home? O [Amazon Echo Dot 5ª geração](https://www.amazon.es/dp/B09B8X9RGM?tag=casainteli0e7-21) é o ponto de partida perfeito."""
    elif "colunas" in title.lower() or "speaker" in title.lower():
        return """## TL;DR — Principais Conclusões

- Amazon Echo Dot 5ª geração é a melhor relação qualidade-preço (35-50€)
- Google Nest Audio oferece o melhor som pelo preço (70-90€)
- Apple HomePod Mini é ideal para utilizadores do ecossistema Apple (100-110€)
- Amazon Echo Studio é a melhor para som de alta fidelidade (180-220€)
- Todos funcionam com Spotify, mas Alexa e Google têm melhor integração

## Introdução

Escolher a coluna inteligente certa pode ser complicado. Amazon, Google e Apple competem neste mercado com propostas diferentes, cada uma com os seus pontos fortes. Neste review, comparamos os modelos principais para o ajudar a decidir qual comprar em 2026.

## Amazon Echo Dot 5ª geração

A [Amazon Echo Dot 5ª geração](https://www.amazon.es/dp/B09B8X9RGM?tag=casainteli0e7-21) continua a ser a coluna inteligente mais vendida em Portugal, e por boas razões.

**Prós:**
- Preço imbatível (35-50€ em promoção)
- Excelente qualidade de som para o tamanho
- Sensor de temperatura integrado
- Alexa em português de Portugal
- Milhares de Skills disponíveis
- Compatível com a maioria dos dispositivos smart home

**Contras:**
- Som não preenche salas grandes
- Design simples (apenas tecido)
- Privacidade: microfones sempre à escuta

## Google Nest Audio

O Google Nest Audio é a alternativa direta ao Echo Dot, com foco na qualidade de som.

**Prós:**
- Melhor som da categoria (50W vs 30W do Echo Dot)
- Design premium em tecido reciclado
- Integração com serviços Google (Calendar, Maps, Gmail)
- Assistant em português

**Contras:**
- Mais caro (70-90€)
- Menos dispositivos smart home compatíveis
- Ecrã disponível apenas no Nest Hub

## Apple HomePod Mini

Para quem já está investido no ecossistema Apple, o HomePod Mini é a escolha natural.

**Prós:**
- Som surpreendentemente bom para o tamanho
- Integração perfeita com iPhone, iPad e Mac
- Siri funciona bem com HomeKit
- Design compacto e elegante

**Contras:**
- Preço elevado (100-110€)
- Limitado a utilizadores Apple
- Menos compatibilidade smart home

## Tabela comparativa

| Característica | Echo Dot 5ª gen | Google Nest Audio | HomePod Mini | Echo Studio |
|---------------|----------------|-------------------|--------------|-------------|
| Preço | 35-50€ | 70-90€ | 100-110€ | 180-220€ |
| Potência | 30W | 50W | N/A | 330W |
| Assistente | Alexa | Google Assistant | Siri | Alexa |
| Zigbee hub | Sim | Não | Não | Sim |
| Sensor temp. | Sim | Não | Sim | Sim |
| Áudio multiroom | Sim | Sim | Sim | Sim |
| Entrada áudio | Não | Não | Não | 3.5mm + ótica |

## Qual escolher conforme o seu ecossistema

- **Utilizador Amazon Prime** — Echo Dot ou Echo Studio (melhor integração com Prime Music, Video e compras)
- **Utilizador Google** — Nest Audio (Calendar, Gmail, Maps integrados)
- **Utilizador Apple** — HomePod Mini (AirPlay, Handoff, HomeKit)
- **Apenas quer bom som** — Echo Studio (melhor som global)
- **Orçamento limitado** — Echo Dot 5ª gen (melhor relação qualidade-preço)

## Veredito final

A [Amazon Echo Dot 5ª geração](https://www.amazon.es/dp/B09B8X9RGM?tag=casainteli0e7-21) é a nossa escolha para a maioria das pessoas. Oferece o melhor equilíbrio entre preço, funcionalidades e qualidade de som.

Se o som é a sua prioridade máxima, o Google Nest Audio ou o Echo Studio são melhores escolhas. Para utilizadores Apple, o HomePod Mini vale o investimento extra.

**Recomendação**: Comece com um Echo Dot e expanda conforme necessário."""
    else:
        return """## TL;DR — Principais Conclusões

- Xiaomi/Aqara oferece melhor qualidade de construção e design premium
- Tuya/Smart Life tem mais opções de baixo custo e maior variedade
- Ambos funcionam com Alexa e Google Home — compatibilidade não é problema
- Para Home Assistant, Xiaomi via Zigbee tem integração mais estável
- Pode misturar dispositivos de ambos os ecossistemas sem problemas

## Introdução

Xiaomi (através da sua submarca Aqara) e Tuya (através da app Smart Life) são dois dos maiores ecossistemas de casa inteligente do mundo. Ambos oferecem dezenas de dispositivos a preços acessíveis, mas com abordagens diferentes. Nesta comparação, analisamos tudo o que precisa de saber para escolher o melhor para si.

## Xiaomi/Aqara: vantagens e desvantagens

A Xiaomi entrou no mercado de casa inteligente através da Aqara, focando-se em qualidade de construção e design.

**Prós:**
- Materiais premium (vidro, alumínio, plástico de alta qualidade)
- Design minimalista e elegante
- Gateway Zigbee muito estável
- Sensores precisos e rápidos
- Integração robusta com Home Assistant

**Contras:**
- Preço ligeiramente superior
- Menor variedade de produtos
- App Mi Home pode ser confusa
- Dependência de cloud chinesa em alguns dispositivos

## Tuya/Smart Life: vantagens e desvantagens

A Tuya é uma plataforma aberta que dezenas de marcas utilizam, resultando numa vasta gama de produtos.

**Prós:**
- Preços muito competitivos
- Grande variedade de dispositivos
- App Smart Life intuitiva
- Funciona com Alexa, Google e Siri
- Suporta Matter nos dispositivos mais recentes

**Contras:**
- Qualidade de construção variável
- Design nem sempre premium
- Dependência de cloud para muitas funções
- Suporte ao cliente inconsistente

## Comparação de sensores

| Tipo | Xiaomi Aqara | Tuya (marca média) |
|------|-------------|-------------------|
| Sensor porta/janela | 12-18€ | 8-12€ |
| Sensor movimento | 15-20€ | 10-15€ |
| Sensor temperatura/humidade | 12-16€ | 8-12€ |
| Sensor de fumo | 30-40€ | 20-30€ |
| Botão inteligente | 15-20€ | 10-15€ |

## Comparação de lâmpadas

| Característica | Xiaomi Yeelight | Tuya (genérica) |
|---------------|----------------|-----------------|
| Preço lâmpada colorida | 20-30€ | 12-20€ |
| Lumens | 800-1100 lm | 600-900 lm |
| Temperatura cor | 2700K-6500K | 2700K-6500K |
| Zigbee/WiFi | Zigbee | WiFi/Zigbee |
| App | Mi Home | Smart Life |

## Comparação de câmaras

| Característica | Xiaomi 360 | Tuya (genérica) |
|---------------|-----------|-----------------|
| Resolução | 2K (2560x1440) | 1080p-2K |
| Visão noturna | Sim (infravermelhos) | Sim |
| Gravação cloud | Sim (paga) | Sim (paga) |
| Gravação local | Cartão SD | Cartão SD |
| Deteção movimento | Sim + IA | Sim |
| Preço | 35-50€ | 25-40€ |

## Compatibilidade com Alexa, Google e HomeKit

**Com Alexa**: Ambos funcionam perfeitamente. A Xiaomi requer o skill "Xiaomi Home" ou "Aqara Home". A Tuya usa o skill "Smart Life".

**Com Google Home**: Funciona bem em ambos. Xiaomi precisa de vincular conta Mi Home. Tuya usa conta Smart Life.

**Com HomeKit**: Xiaomi Aqara tem hubs compatíveis com HomeKit. Tuya oferece alguns dispositivos com suporte nativo HomeKit.

## Home Assistant: qual funciona melhor?

Para utilizadores de Home Assistant:

- **Xiaomi Aqara**: Integração via gateway Zigbee é excelente. O addon Xiaomi Gateway 3 permite controlo local completo sem cloud.
- **Tuya**: A integração oficial da Tuya para Home Assistant funciona mas tem quotas de API limitadas. A alternativa local (Tuya Local) funciona para alguns dispositivos WiFi.

**Veredito**: Xiaomi Aqara ganha para Home Assistant pela integração local mais estável.

## Qual escolher em 2026?

**Escolha Xiaomi Aqara se:**
- Valoriza qualidade de construção
- Usa Home Assistant
- Prefere design premium
- Quer sensores mais precisos

**Escolha Tuya se:**
- Tem orçamento limitado
- Quer maior variedade de produtos
- Prefere a app Smart Life
- Quer experimentar sem grande investimento

Ambos os ecossistemas são excelentes. A boa notícia é que não precisa de escolher apenas um — pode [misturar dispositivos](https://www.amazon.es/dp/B0H2V9Q87H?tag=casainteli0e7-21) e usar o assistente que preferir para controlar tudo."""
    return ""

def generate_article(article_def):
    body = get_pt_article_body(article_def["title"])
    today = datetime.date.today()
    disclosure = "Este artigo contém links de afiliados. Poderemos receber uma comissão por compras efetuadas através destes links, sem custo adicional para si."

    frontmatter = {
        "title": article_def["title"],
        "date": today.isoformat(),
        "category": article_def["category"],
        "excerpt": article_def["excerpt"],
        "author": "Equipa Casa Inteligente PT",
        "tags": article_def["tags"],
        "featured": article_def.get("featured", False),
        "affiliate_link": article_def.get("affiliate_link", ""),
        "affiliate_disclosure": disclosure,
        "cta_text": article_def.get("cta_text", ""),
        "product_id": article_def.get("product_id", ""),
        "faq": article_def.get("faq", []),
    }

    yaml_front = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = f"---\n{yaml_front}---\n\n{body.strip()}\n"
    target_dir = CONTENT_DIR / article_def["lang"] / article_def["subdir"]
    target_dir.mkdir(parents=True, exist_ok=True)
    filepath = target_dir / f"{article_def['id']}.md"
    filepath.write_text(content, encoding="utf-8")
    print(f"  [OK] {filepath.relative_to(ROOT)}")
    return filepath

def generate_all():
    print("[TEMPLATE] Generating realistic template-based content...\n")
    count = 0
    for article in ARTICLES:
        target_file = CONTENT_DIR / article["lang"] / article["subdir"] / f"{article['id']}.md"
        if target_file.exists():
            content = target_file.read_text(encoding="utf-8")
            if "# Draft Content" not in content and "TL;DR" in content:
                print(f"  [SKIP] {article['id']} — already has real content")
                continue
        generate_article(article)
        count += 1
    print(f"\n[TEMPLATE] Generated {count} article(s)")
    return count

if __name__ == "__main__":
    generate_all()
