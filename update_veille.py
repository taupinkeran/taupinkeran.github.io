import feedparser
import datetime
import re

FEEDS = [
    # Flux spécialisés Jeu Vidéo & Gamedev
    "https://www.gamedeveloper.com/rss.xml",
    "https://gamefromscratch.com/feed/",
    "https://www.gamekult.com/feed.xml",
    "https://www.jeuxvideo.com/rss/rss.xml",
    # Flux Tech & IA (axés développement)
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://www.developpez.com/index/rss"
]

KEYWORDS = [
    # IA Générative & Assistants
    "ia générative", "generative ai", "chatgpt", "gemini", "claude", "copilot", 
    "llm", "intelligence artificielle", "ai agent", "npc ai",
    # Moteurs de jeux & Développement spécialisé
    "jeu vidéo", "video game", "game dev", "gamedev", "unreal engine", "unity", 
    "godot", "moteur de jeu", "asset generation", "procedural generation",
    "procedural content", "game design", "3d generation"
]

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80"

def extract_image(entry):
    """ Tente d'extraire l'URL d'une image de l'article RSS """
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

    return DEFAULT_IMAGE

def fetch_articles():
    articles = []
    seen_titles = set()

    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get('title', '')
                summary = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', '')
                published = entry.get('published', entry.get('updated', ''))

                if title in seen_titles:
                    continue

                content = f"{title} {summary}".lower()
                
                # Vérifie la présence conjointe/pertinente des mots-clés liés au gamedev
                if any(kw in content for kw in KEYWORDS):
                    image_url = extract_image(entry)
                    clean_summary = re.sub('<[^<]+?>', '', summary)
                    clean_summary = " ".join(clean_summary.split())[:140] + '...'

                    articles.append({
                        'title': title,
                        'link': link,
                        'summary': clean_summary if len(clean_summary) > 5 else "Consulter l'article pour plus de détails.",
                        'image': image_url,
                        'date': published[:16] if published else "Récent"
                    })
                    seen_titles.add(title)
        except Exception as e:
            print(f"Erreur sur le flux {url}: {e}")

    return articles[:12] # Récupère les 12 articles les plus récents

def update_html():
    articles = fetch_articles()
    
    if not articles:
        articles_html = '<p class="section-desc">Aucun article trouvé pour le moment sur le développement vidéoludique et l\'IA.</p>'
    else:
        articles_html = '<div class="news-grid">\n'
        for art in articles:
            articles_html += f'''
            <div class="news-card">
                <img src="{art['image']}" alt="Illustration article" class="news-image" loading="lazy" onerror="this.src='{DEFAULT_IMAGE}'">
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
        with open("veille.html", "r", encoding="utf-8") as f:
            content = f.read()

        pattern = r"<!-- START_AUTOMATIC_ARTICLES -->.*?<!-- END_AUTOMATIC_ARTICLES -->"
        replacement = f"<!-- START_AUTOMATIC_ARTICLES -->\n{articles_html}\n<!-- END_AUTOMATIC_ARTICLES -->"
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        with open("veille.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("veille.html mis à jour avec succès (Focus 100% Jeu Vidéo & IA) !")
    except Exception as e:
        print(f"Erreur lors de la mise à jour : {e}")

if __name__ == "__main__":
    update_html()
