import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from bs4 import BeautifulSoup

# Mini-serwer dla Render.com
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot OLX dziala 24/7!")

def run_http_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

WEBHOOK_URL = "TUTAJ_WKLEJ_LINK_DO_WEBHOOKA_DISCORD"
OLX_URL = "https://www.olx.pl/elektronika/telefony/smartfony-telefony/poznan/?search%5Border%5D=created_at%3Adesc"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7"
}

seen_ids = set()

print("--- BOT STARTUJE ---", flush=True)

def get_latest_ads():
    try:
        response = requests.get(OLX_URL, headers=headers, timeout=10)
        print(f"Status odpowiedzi OLX: {response.status_code}", flush=True)
        
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
        print("Błąd pobierania:", e, flush=True)
        return []

# Inicjalizacja początkowa
initial_ads = get_latest_ads()
print(f"Pobrano początkowych ogłoszeń: {len(initial_ads)}", flush=True)
for ad in initial_ads:
    seen_ids.add(ad['id'])

while True:
    try:
        current_ads = get_latest_ads()
        for ad in current_ads:
            if ad['id'] not in seen_ids:
                print(f"Nowość wykryta: {ad['title']}", flush=True)
                data = {
                    "content": f"🚨 **Nowy iPhone w Poznaniu!**\n📌 **{ad['title']}**\n🔗 {ad['link']}"
                }
                requests.post(WEBHOOK_URL, json=data)
                seen_ids.add(ad['id'])
                  
        time.sleep(30)
    except Exception as e:
        print("Błąd w pętli głównej:", e, flush=True)
        time.sleep(30)
