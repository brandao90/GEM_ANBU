# GEM_ANBU v8.1 – 24/7 + CoinGecko + Zero erro
import os, time, requests, sqlite3, schedule
from datetime import datetime, timedelta
from threading import Thread
from flask import Flask
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT  = os.getenv("TELEGRAM_CHAT_ID")
DB    = "/tmp/gem_anbu.db" if "RENDER" in os.environ else "gem_anbu.db"

app = Flask(__name__)

def br(): return (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M")
def send(m): requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT, "text": m, "parse_mode":"HTML", "disable_web_page_preview":True}).raise_for_status()

def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS s (name TEXT PRIMARY KEY)")

init_db()

def job():
    gems = []
    # CoinGecko
    try:
        r = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1")
        for t in r.json():
            if t["market_cap"] >= 100000:
                name = t["name"]
                sym  = t["symbol"].upper()
                cap  = t["market_cap"]
                with sqlite3.connect(DB) as c:
                    if c.execute("SELECT 1 FROM s WHERE name=?",(name,)).fetchone(): continue
                    c.execute("INSERT INTO s VALUES (?)",(name,))
                gems.append(f"CG <b>{name} (${sym})</b>\nMC: ${cap:,.0f}\n<a href='https://coingecko.com/en/coins/{t['id']}'>Ver</a>")
    except: pass

    # DexScreener
    try:
        r = requests.get("https://api.dexscreener.com/latest/dex/search?q=new").json()["pairs"][:10]
        for p in r:
            n = p["baseToken"]["name"]
            s = p["baseToken"]["symbol"]
            c = float(p.get("fdv") or 0)
            l = p["liquidity"]["usd"]
            if c >= 100000 and l >= 10000:
                with sqlite3.connect(DB) as con:
                    if con.execute("SELECT 1 FROM s WHERE name=?",(n,)).fetchone(): continue
                    con.execute("INSERT INTO s VALUES (?)",(n,))
                gems.append(f"DEX <b>{n} (${s})</b>\nMC: ${c:,.0f} | Liq: ${l:,.0f}\n<a href='{p['url']}'>Ver</a>")
    except: pass

    msg = "<b>GEM_ANBU v8.1</b>\n\n" + "\n\n".join(gems[:20]) + f"\n\n<i>{br()}</i>" if gems else "Nada novo agora."
    try: send(msg)
    except: pass

@app.route("/")
def home():
    return "GEM_ANBU v8.1 24/7 ATIVO", 200

def web():
    app.run(host="0.0.0.0", port=os.getenv("PORT",8080))

def start():
    last = None
    while True:
        try:
            u = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", params={"offset":last}).json()["result"]
            for x in u:
                last = x["update_id"]+1
                if x.get("message",{}).get("text","") == "/start":
                    send("<b>GEM_ANBU ATIVADO!</b>\nGems ≥ $100k + $10k liq\nA cada hora\n\n"+msg)
                    job()
            time.sleep(5)
        except: time.sleep(10)

if __name__ == "__main__":
    init_db()
    Thread(target=web,daemon=True).start()
    Thread(target=start,daemon=True).start()
    schedule.every(60).minutes.do(job)
    job()
    while True:
        schedule.run_pending()
        time.sleep(30)
