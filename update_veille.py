import feedparser
import datetime
import re

# Flux RSS ciblés : Jeu Vidéo, IA et Cybersécurité
FEEDS = [
    "https://www.gamedeveloper.com/rss.xml",
    "https://gamefromscratch.com/feed/",
    "https://www.zerodayinitiative.com/rss/published/",
    "https://www.bleepingcomputer.com/feed/"
]

KEYWORDS = ["ai", "ia", "intelligence artificielle", "security", "vulnerability", "exploit", "unreal", "unity", "game"]

def fetch_articles():
    articles = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            link = entry.get('link', '')
            published = entry.get('published', '')

            content = f"{title} {summary}".lower()
            if any(kw in content for kw in KEYWORDS):
                # Nettoyage sommaire des balises HTML dans le résumé
                clean_summary = re.sub('<[^<]+?>', '', summary)[:180] + '...'
                articles.append({
                    'title': title,
                    'link': link,
                    'summary': clean_summary,
                    'date': published
                })
    return articles[:12] # Top 12 des plus récents

def update_html():
    articles = fetch_articles()
    
    # Génération du bloc HTML pour les articles
    articles_html = '<div class="articles-grid">\n'
    for art in articles:
        articles_html += f'''
        <article class="article-card">
            <h3><a href="{art['link']}" target="_blank" rel="noopener">{art['title']}</a></h3>
            <p>{art['summary']}</p>
            <span class="date">Publié le : {art['date']}</span>
        </article>
        '''
    articles_html += '</div>\n'
    articles_html += f'<p class="last-update">Dernière mise à jour automatique : {datetime.datetime.now().strftime("%d/%m/%Y à %H:%M UTC")}</p>'

    # Injection dans veille.html entre les balises de commentaires
    try:
        with open("veille.html", "r", encoding="utf-8") as f:
            content = f.read()

        pattern = r"<!-- START_AUTOMATIC_ARTICLES -->.*?<!-- END_AUTOMATIC_ARTICLES -->"
        replacement = f"<!-- START_AUTOMATIC_ARTICLES -->\n{articles_html}\n<!-- END_AUTOMATIC_ARTICLES -->"
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        with open("veille.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("veille.html mis à jour avec succès.")
    except Exception as e:
        print(f"Erreur lors de la mise à jour : {e}")

if __name__ == "__main__":
    update_html()