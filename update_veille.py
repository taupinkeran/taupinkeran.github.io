import feedparser
import datetime
import re

FEEDS = [
    # Flux Francophones
    "https://www.lemagit.fr/rss/RSS-Syndication.xml",
    "https://www.zataz.com/feed/",
    "https://www.clubic.com/feed/news.rss",
    "https://kulturegeek.fr/feed",
    "https://www.gamekult.com/feed.xml",
    "https://www.jeuxvideo.com/rss/rss.xml",
    # Flux Internationaux / Anglais spécialisés Jeu Vidéo & Sécurité
    "https://www.gamedeveloper.com/rss.xml",
    "https://gamefromscratch.com/feed/",
    "https://www.bleepingcomputer.com/feed/"
]

KEYWORDS = [
    "ia", "intelligence artificielle", "sécurité", "faille", "cybersécurité", 
    "unreal", "unity", "jeu vidéo", "piratage", "vulnerabilite", "pentest", 
    "moteur de jeu", "chatgpt", "gemini", "copilot", "ai", "security", "exploit"
]

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80"

def extract_image(entry):
    """ Tente d'extraire l'URL d'une image de l'article RSS """
    # 1. Vérifie dans media_content
    if 'media_content' in entry and len(entry.media_content) > 0:
        if 'url' in entry.media_content[0]:
            return entry.media_content[0]['url']
    
    # 2. Vérifie dans enclosures
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        for enc in entry.enclosures:
            if enc.get('type', '').startswith('image/'):
                return enc.get('href', '')

    # 3. Cherche une balise <img> dans la description/summary
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

    return articles[:12] # Récupère jusqu'à 12 articles

def update_html():
    articles = fetch_articles()
    
    if not articles:
        articles_html = '<p class="section-desc">Aucun article n\'a été trouvé cette semaine.</p>'
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
        print("veille.html mis à jour avec succès avec des cartes d'articles et images !")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    update_html()
