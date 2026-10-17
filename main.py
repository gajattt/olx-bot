import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot OLX dziala 24/7!")

def run_http_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

WEBHOOK_URL = "https://discord.com/api/webhooks/1560940211859357696/CmEPHq6Tb5hdI42lUKJV44bH6nqKn2Xo9icu-9Ov3dqRjCTMfm6GR0HqxSScm8laWrYf"

TARGET_OLX = "https://www.olx.pl/elektronika/telefony/smartfony-telefony/poznan/?search%5Border%5D=created_at%3Adesc"


OLX_URL = f"https://api.allorigins.win/raw?url={requests.utils.quote(TARGET_OLX)}"

# Bardziej zaawansowane nagłówki udające prawdziwą przeglądarkę
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}

seen_ids = set()

def get_latest_ads():
    try:
        # Używamy sesji, aby zachować ciasteczka
        session = requests.Session()
        response = session.get(OLX_URL, headers=headers, timeout=10)
        print(f"Status OLX: {response.status_code}", flush=True)
        
        if response.status_code != 200:
            print("OLX nadal blokuje zapytanie (403/503).", flush=True)
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        ads = []
        
        cards = soup.select('div[data-cy="l-card"]')
        if not cards:
            cards = soup.select('[data-testid="l-card"]')
            
        print(f"Znaleziono kart na stronie: {len(cards)}", flush=True)
        
        for card in cards:
            title_elem = card.find('h4') or card.find('h6')
            link_elem = card.find('a')
            
            if title_elem and link_elem and link_elem.has_attr('href'):
                title = title_elem.text.strip()
                href = link_elem['href']
                link = "https://www.olx.pl" + href if href.startswith('/') else href
                
                if '-ID' in link:
                    try:
                        ad_id = link.split('-ID')[-1].split('.')[0]
                        ads.append({
                            "id": ad_id,
                            "title": title,
                            "link": link
                        })
                    except:
                        continue
        return ads
    except Exception as e:
        print("Błąd pobierania:", e, flush=True)
        return []

print("--- STARTUJEMY TEST POBIERANIA ---", flush=True)
initial_ads = get_latest_ads()
print(f"Początkowo wykrytych ogłoszeń: {len(initial_ads)}", flush=True)
for ad in initial_ads:
    seen_ids.add(ad['id'])

while True:
    try:
        current_ads = get_latest_ads()
        for ad in current_ads:
            if ad['id'] not in seen_ids:
                print(f"Nowość! Wysyłam: {ad['title']}", flush=True)
                data = {
                    "content": f"🚨 **Nowy iPhone w Poznaniu!**\n📌 **{ad['title']}**\n🔗 {ad['link']}"
                }
                requests.post(WEBHOOK_URL, json=data)
                seen_ids.add(ad['id'])
                  
        time.sleep(45) # Nieco dłuższy interwał, żeby rzadziej odpytywać serwer
    except Exception as e:
        print("Błąd w pętli:", e, flush=True)
        time.sleep(45)
