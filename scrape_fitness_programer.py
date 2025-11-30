import requests
from bs4 import BeautifulSoup
import os
import time

BASE_URL = "https://fitnessprogramer.com"
MUSCLE_GROUPS = {
    "chest": "https://fitnessprogramer.com/exercise-primary-muscle/chest/",
    "shoulders": "https://fitnessprogramer.com/exercise-primary-muscle/shoulders/",
    "back": "https://fitnessprogramer.com/exercise-primary-muscle/back/",
    "biceps": "https://fitnessprogramer.com/exercise-primary-muscle/biceps/",
    "triceps": "https://fitnessprogramer.com/exercise-primary-muscle/triceps/",
    "legs": "https://fitnessprogramer.com/exercise-primary-muscle/leg/",
    "abs": "https://fitnessprogramer.com/exercise-primary-muscle/abs/"
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Treino de {title}</title>
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#34495e">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #ecf0f1; color: #2c3e50; }}
        header {{ background: #2c3e50; color: white; padding: 15px; text-align: center; }}
        .container {{ max-width: 800px; margin: 20px auto; padding: 0 15px; }}
        .exercise-card {{ background: white; margin-bottom: 20px; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }}
        .exercise-card h2 {{ color: #e67e22; margin-top: 0; }}
        .exercise-card img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 15px 0; }}
        .exercise-info {{ display: flex; justify-content: space-around; background: #f9f9f9; padding: 10px; border-radius: 6px; margin-top: 10px; }}
        .exercise-info div {{ font-weight: bold; }}
        .back-link {{ display: block; text-align: center; margin: 20px; color: #2c3e50; text-decoration: none; font-weight: bold; font-size: 1.1em; }}
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>

<header>
    <h1>Treino de {title}</h1>
    <p>Top 5 Exercícios</p>
</header>

<div class="container">
    {content}
    <a href="index.html" class="back-link">← Voltar para o Guia Principal</a>
</div>

</body>
</html>"""

def get_exercises(url):
    print(f"Fetching {url}...")
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    exercises = []
    # Based on observation, exercise links are likely in h2 tags inside article or similar containers
    # We'll look for links that contain '/exercise/' in their href
    links = soup.find_all('a', href=True)
    count = 0
    
    seen_urls = set()
    
    for link in links:
        href = link['href']
        # Check if it looks like an exercise URL
        if '/exercise/' in href and href not in seen_urls:
            # Skip pagination or other irrelevant links
            if 'page/' in href:
                continue
                
            # Try to get a title
            title = link.get('title')
            if not title:
                title = link.get_text(strip=True)
            
            # If still no title or it's generic like "View Details", skip or try to find parent header
            if not title or title.lower() == 'view details':
                continue
                
            # Heuristic: Exercise titles are usually longer than 3 chars
            if len(title) < 3:
                continue

            print(f"  Found potential exercise: {title} ({href})")
            seen_urls.add(href)
            exercises.append({'title': title, 'url': href})
            count += 1
            if count >= 5:
                break
    
    return exercises

def get_gif_url(exercise_url):
    print(f"  Fetching details for {exercise_url}...")
    response = requests.get(exercise_url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the GIF
    imgs = soup.find_all('img', src=True)
    for img in imgs:
        src = img['src']
        if src.lower().endswith('.gif'):
            return src
    return None

def download_gif(url, save_path):
    if not url:
        return False
    try:
        if os.path.exists(save_path):
            print(f"    File already exists: {save_path}")
            return True
            
        print(f"    Downloading {url}...")
        response = requests.get(url, headers=HEADERS)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"    Error downloading {url}: {e}")
        return False

def main():
    base_download_dir = os.path.join(os.getcwd(), 'downloads')
    if not os.path.exists(base_download_dir):
        os.makedirs(base_download_dir)

    for muscle, url in MUSCLE_GROUPS.items():
        print(f"\nProcessing {muscle}...")
        
        # Create directory for this muscle group
        muscle_dir = os.path.join(base_download_dir, muscle)
        if not os.path.exists(muscle_dir):
            os.makedirs(muscle_dir)
            
        exercises = get_exercises(url)
        
        html_content = ""
        
        for i, ex in enumerate(exercises):
            gif_url = get_gif_url(ex['url'])
            if gif_url:
                filename = f"{ex['title'].replace(' ', '_').replace('/', '-').lower()}.gif"
                save_path = os.path.join(muscle_dir, filename)
                
                if download_gif(gif_url, save_path):
                    # Relative path for HTML
                    rel_path = f"downloads/{muscle}/{filename}"
                    
                    html_content += f"""
    <div class="exercise-card">
        <h2>{i+1}. {ex['title']}</h2>
        <img src="{rel_path}" alt="{ex['title']}">
        <div class="exercise-info">
            <div>Séries: 3</div>
            <div>Reps: 10-12</div>
            <div>Descanso: 60"</div>
        </div>
    </div>"""
            
            time.sleep(1) # Be nice to the server

        # Generate HTML file
        final_html = HTML_TEMPLATE.format(title=muscle.capitalize(), content=html_content)
        html_filename = f"treino_{muscle}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"Created {html_filename}")

if __name__ == "__main__":
    main()
