import feedparser
import datetime
import re

# Sources d'actualités francophones (Sécurité, Tech, Jeux Vidéo)
FEEDS = [
    # Cybersécurité & Tech FR
    "https://www.lemagit.fr/rss/RSS-Syndication.xml",
    "https://www.zataz.com/feed/",
    "https://www.clubic.com/feed/news.rss",
    "https://kulturegeek.fr/feed",
    # Jeux Vidéo & Tech FR
    "https://www.gamekult.com/feed.xml",
    "https://www.jeuxvideo.com/rss/rss.xml"
]

# Mots-clés en français et anglais fréquemment utilisés dans les flux FR
KEYWORDS = [
    "ia", "intelligence artificielle", "sécurité", "faille", "cybersécurité", 
    "unreal", "unity", "jeu vidéo", "jeux vidéo", "piratage", "vulnerabilite",
    "pentest", "moteur de jeu", "chatgpt", "gemini", "copilot"
]

def fetch_articles():
    articles = []
    seen_titles = set() # Pour éviter les doublons

    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get('title', '')
                summary = entry.get('summary', entry.get('description', ''))
                link = entry.get('link', '')
                published = entry.get('published', entry.get('updated', ''))

                # Éviter les doublons exacts de titre
                if title in seen_titles:
                    continue

                content = f"{title} {summary}".lower()
                
                # Vérification de la présence d'au moins un mot-clé
                if any(kw in content for kw in KEYWORDS):
                    # Nettoyage des balises HTML dans la description
                    clean_summary = re.sub('<[^<]+?>', '', summary)
                    # Supprimer les retours à la ligne superflus
                    clean_summary = " ".join(clean_summary.split())[:160] + '...'
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'summary': clean_summary if len(clean_summary) > 5 else "Cliquez sur l'article pour en savoir plus.",
                        'date': published[:16] if published else "Récent"
                    })
                    seen_titles.add(title)
        except Exception as e:
            print(f"Erreur lors de la lecture du flux {url}: {e}")

    return articles[:9] # Top 9 des articles francophones les plus récents

def update_html():
    articles = fetch_articles()
    
    if not articles:
        articles_html = '<p class="section-desc">Aucun article récent correspondant aux critères n\'a été trouvé cette semaine.</p>'
    else:
        # Construction du HTML adapté à ta DA (skills-grid et skill-card)
        articles_html = '<div class="skills-grid">\n'
        for art in articles:
            articles_html += f'''
            <div class="skill-card">
                <div class="tech-name">
                    <a href="{art['link']}" target="_blank" rel="noopener" style="color: var(--accent); text-decoration: none;">{art['title']}</a>
                </div>
                <div class="tech-desc" style="margin-top: 0.5rem;">{art['summary']}</div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.75rem;">Publié : {art['date']}</div>
            </div>
            '''
        articles_html += '</div>\n'
    
    articles_html += f'<p class="section-desc" style="margin-top: 1rem; font-size: 0.8rem;">Dernière synchronisation automatique : {datetime.datetime.now().strftime("%d/%m/%Y à %H:%M UTC")}</p>'

    try:
        with open("veille.html", "r", encoding="utf-8") as f:
            content = f.read()

        pattern = r"<!-- START_AUTOMATIC_ARTICLES -->.*?<!-- END_AUTOMATIC_ARTICLES -->"
        replacement = f"<!-- START_AUTOMATIC_ARTICLES -->\n{articles_html}\n<!-- END_AUTOMATIC_ARTICLES -->"
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        with open("veille.html", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("veille.html mis à jour avec succès avec des articles en français !")
    except Exception as e:
        print(f"Erreur lors de la mise à jour : {e}")

if __name__ == "__main__":
    update_html()
