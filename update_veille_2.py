import feedparser
import datetime
import re
import urllib.parse

FEEDS = [
    "https://www.gamedeveloper.com/rss.xml",
    "https://gamefromscratch.com/feed/",
    "https://www.clubic.com/feed/news.rss"
]

KEYWORDS = [
    "ia", "intelligence artificielle", "sécurité", "faille", "cybersécurité", 
    "unreal", "unity", "jeu vidéo", "piratage", "vulnerabilite", "pentest", 
    "chatgpt", "gemini", "ai", "security", "exploit", "roblox", "epic"
]

def clean_html_text(text):
    if not text:
        return ""
    clean = re.sub(r'<[^<]+?>', '', text)
    clean = " ".join(clean.split())
    return clean

def get_dynamic_image(title):
    keywords = ["security", "cyber", "code", "ai", "hacker", "gaming"]
    title_lower = title.lower()
    selected_kw = "tech"
    for kw in keywords:
        if kw in title_lower:
            selected_kw = kw
            break
    return f"https://source.unsplash.com/featured/600x400/?{selected_kw}&sig={hash(title)}"

def extract_image(entry, title):
    if 'media_content' in entry and len(entry.media_content) > 0:
        if 'url' in entry.media_content[0]:
            return entry.media_content[0]['url']
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'):
                return enc.get('href', '')
    content = entry.get('summary', '') or entry.get('description', '')
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    if img_match:
        return img_match.group(1)
    return get_dynamic_image(title)

def fetch_articles():
    articles = []
    seen_titles = set()

    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get('title', '')
                raw_summary = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', '')
                published = entry.get('published', entry.get('updated', ''))

                if title in seen_titles:
                    continue

                content_to_check = f"{title} {raw_summary}".lower()
                if any(kw in content_to_check for kw in KEYWORDS):
                    clean_summary = clean_html_text(raw_summary)
                    if len(clean_summary) > 130:
                        clean_summary = clean_summary[:130] + '...'

                    image_url = extract_image(entry, title)

                    articles.append({
                        'title': title,
                        'link': link,
                        'summary': clean_summary if len(clean_summary) > 10 else "Consulter l'article pour plus de détails.",
                        'image': image_url,
                        'date': published[:16] if published else "Récent"
                    })
                    seen_titles.add(title)
        except Exception as e:
            print(f"Erreur flux {url}: {e}")

    return articles[:12]

def generate_synthesis(articles):
    """ Génère une synthèse textuelle dynamique basée sur les articles récupérés """
    if not articles:
        return "Aucune donnée récente à synthétiser pour cette période."

    # Analyse rapide des thèmes présents dans les titres
    titles_text = " ".join([art['title'] for art in articles]).lower()
    
    themes = []
    if "ai" in titles_erté or "ia" in titles_text or "artificial" in titles_text:
        themes.append("l'intégration croissante des assistants et outils d'intelligence artificielle dans les moteurs de jeux (comme Unreal Engine ou Unity)")
    if "security" in titles_text or "cloning" in titles_text or "vulnerability" in titles_text:
        themes.append("les préoccupations grandissantes concernant la sécurité, le clonage de jeux par IA et la protection des données des studios")
    if "roblox" in titles_text or "epic" in titles_text:
        themes.append("les choix stratégiques des géants de l'industrie (Epic, Roblox, Google) vers des environnements de développement automatisés")

    themes_str = "; ".join(themes) if themes else "l'évolution des pratiques de développement et des technologies émergentes"

    synthesis_html = f"""
    <div style="background-color: var(--bg-card); padding: 1.75rem; border-radius: 0.75rem; border: 1px solid var(--accent); margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(56, 189, 248, 0.1);">
        <h3 style="color: var(--accent); margin-top: 0; font-size: 1.15rem; display: flex; align-items: center; gap: 0.5rem;">
            🤖 Synthèse Automatique de la Semaine
        </h3>
        <p style="color: var(--text-main); font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">
            Cette semaine, l'analyse de nos flux de veille met en lumière {themes_str}. À travers les {len(articles)} articles recensés, on observe un impact direct sur la structuration des projets vidéoludiques et la nécessité pour les développeurs d'adapter leurs méthodes face à ces mutations technologiques.
        </p>
    </div>
    """
    return synthesis_html

def update_html():
    articles = fetch_articles()
    
    # 1. Génération de la synthèse dynamique
    synthesis_html = generate_synthesis(articles)

    # 2. Génération des cartes d'articles
    if not articles:
        articles_html = '<p class="section-desc">Aucun article n\'a été trouvé cette semaine.</p>'
    else:
        articles_html = '<div class="news-grid">\n'
        for art in articles:
            articles_html += f'''
            <div class="news-card">
                <img src="{art['image']}" alt="Illustration article" class="news-image" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600'">
                <div class="news-content">
                    <a href="{art['link']}" target="_blank" rel="noopener" class="news-title">{art['title']}</a>
                    <p class="news-desc">{art['summary']}</p>
                    <div class="news-meta">
                        <span>Publié : {art['date']}</span>
                    </div>
                </div>
            </div>
            '''
        articles_html += '</div>\n'

    try:
        with open("veille_2.html", "r", encoding="utf-8") as f:
            content = f.read()

        # Remplacement de la synthèse
        synth_pattern = r"<!-- START_SYNTHESIS -->.*?<!-- END_SYNTHESIS -->"
        synth_replacement = f"<!-- START_SYNTHESIS -->\n{synthesis_html}\n<!-- END_SYNTHESIS -->"
        content = re.sub(synth_pattern, synth_replacement, content, flags=re.DOTALL)

        # Remplacement des articles
        art_pattern = r"<!-- START_AUTOMATIC_ARTICLES -->.*?<!-- END_AUTOMATIC_ARTICLES -->"
        art_replacement = f"<!-- START_AUTOMATIC_ARTICLES -->\n{articles_html}\n<!-- END_AUTOMATIC_ARTICLES -->"
        content = re.sub(art_pattern, art_replacement, content, flags=re.DOTALL)

        with open("veille_2.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Mise à jour réussie : Synthèse dynamique et articles injectés !")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    update_html()
