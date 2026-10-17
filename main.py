import time
import requests
from bs4 import BeautifulSoup

# Wklej tutaj swój skopiowany link webhooka z Discorda w cudzysłowie
WEBHOOK_URL = "https://discord.com/api/webhooks/1560940211859357696/CmEPHq6Tb5hdI42lUKJV44bH6nqKn2Xo9icu-9Ov3dqRjCTMfm6GR0HqxSScm8laWrYf"

# Link z filtrami OLX: Poznań, telefony, od najnowszych
OLX_URL = "https://www.olx.pl/elektronika/telefony/smartfony-telefony/poznan/?search%5Border%5D=created_at%3Adesc"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

seen_ids = set()

def get_latest_ads():
    try:
        response = requests.get(OLX_URL, headers=headers)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        ads = []
        
        for card in soup.select('div[data-cy="l-card"]'):
            title_elem = card.find('h4')
            link_elem = card.find('a')
            
            if title_elem and link_elem:
                title = title_elem.text.strip()
                link = "https://www.olx.pl" + link_elem['href'] if link_elem['href'].startswith('/') else link_elem['href']
                
                try:
                    ad_id = link.split('-ID')[-1].split('.')[0]
                except:
                    continue
                
                ads.append({
                    "id": ad_id,
                    "title": title,
                    "link": link
                })
        return ads
    except Exception as e:
        print("Błąd pobierania:", e)
        return []

def send_discord_notification(ad):
    data = {
        "content": f"🚨 **Nowy iPhone w Poznaniu!**\n📌 **{ad['title']}**\n🔗 {ad['link']}"
    }
    requests.post(WEBHOOK_URL, json=data)

print("Bot ruszył i monitoruje OLX...")

initial_ads = get_latest_ads()
for ad in initial_ads:
    seen_ids.add(ad['id'])

while True:
    try:
        current_ads = get_latest_ads()
        for ad in current_ads:
            if ad['id'] not in seen_ids:
                print(f"Nowość: {ad['title']}")
                send_discord_notification(ad)
                seen_ids.add(ad['id'])
                  
        time.sleep(30)
    except Exception as e:
        print("Błąd w pętli:", e)
        time.sleep(30)
