import feedparser
import re
import urllib.request

# Liste des flux RSS ciblés Jeu Vidéo & IA / Tech
FEEDS = [
    "https://www.gamedeveloper.com/rss.xml",
    "https://gamefromscratch.com/feed/",
    "https://www.gamekult.com/feed.xml",
    "https://www.jeuxvideo.com/rss/rss.xml",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://www.clubic.com/feed/news.rss"
]

KEYWORDS = [
    "ia", "ai", "chatgpt", "gemini", "claude", "copilot", "llm", 
    "unreal", "unity", "godot", "jeu vidéo", "jeu video", "gamedev", 
    "game dev", "moteur", "procedural", "3d", "generation", "npc", "pnj"
]

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80"

def fetch_feed_with_user_agent(url):
    """ Télécharge le flux en se passant pour un navigateur web """
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read()
    except Exception as e:
        print(f"⚠️ Impossible d'accéder au flux {url} : {e}")
        return None

def extract_image(entry):
    """ Extrait l'image d'un article """
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
        content_bytes = fetch_feed_with_user_agent(url)
        if not content_bytes:
            continue

        feed = feedparser.parse(content_bytes)
        print(f"📡 Flux analysé : {url} ({len(feed.entries)} articles trouvés)")

        for entry in feed.entries:
            title = entry.get('title', '')
            summary = entry.get('summary', entry.get('description', ''))
            link = entry.get('link', '')
            published = entry.get('published', entry.get('updated', ''))

            if title in seen_titles:
                continue

            full_text = f"{title} {summary}".lower()
            
            # Vérification des mots-clés
            if any(kw in full_text for kw in KEYWORDS):
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

    return articles[:12]

def update_html():
    articles = fetch_articles()
    print(f"✅ Total d'articles sélectionnés : {len(articles)}")

    if not articles:
        articles_html = '<p class="section-desc">Aucun article n\'a été trouvé actuellement sur ce thème.</p>'
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
        print("🎉 veille.html mis à jour avec succès !")
    except Exception as e:
        print(f"❌ Erreur d'écriture dans veille.html : {e}")

if __name__ == "__main__":
    update_html()
