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
OLX_URL = f"https://api.codetabs.com/v1/proxy?quest={TARGET_OLX}"

seen_ids = set()

def get_latest_ads():
    try:
        # Zwiększamy timeout do 25 sekund, żeby proxy miało czas na odpowiedź
        response = requests.get(OLX_URL, timeout=25)
        print(f"Status OLX: {response.status_code}", flush=True)
        
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        ads = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '-ID' in href or '/d/oferta/' in href:
                link = "https://www.olx.pl" + href if href.startswith('/') else href
                
                title = a.text.strip()
                if not title or len(title) < 5:
                    parent = a.find_parent('div')
                    if parent:
                        h_tag = parent.find(['h4', 'h6', 'p'])
                        if h_tag:
                            title = h_tag.text.strip()
                
                if not title:
                    title = "Nowy iPhone (zobacz na OLX)"

                try:
                    ad_id = link.split('-ID')[-1].split('.')[0]
                    if len(ad_id) < 15:
                        ads.append({
                            "id": ad_id,
                            "title": title[:100],
                            "link": link
                        })
                except:
                    continue
                    
        unique_ads = {ad['id']: ad for ad in ads}.values()
        print(f"Znaleziono unikalnych ogłoszeń: {len(unique_ads)}", flush=True)
        return list(unique_ads)
        
    except Exception as e:
        print("Błąd pobierania (timeout/proxy):", e, flush=True)
        return []

print("--- STARTUJEMY BOTA OLX ---", flush=True)
initial_ads = get_latest_ads()
print(f"Początkowo załadowanych ogłoszeń: {len(initial_ads)}", flush=True)
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
                  
        time.sleep(45)
    except Exception as e:
        print("Błąd w pętli:", e, flush=True)
        time.sleep(45)
