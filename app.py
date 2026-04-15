import os
import redis
import datetime
import random
import requests
import urllib3
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# --- KONFIGURACE ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "tajny-klic-123")

# --- PROMĚNNÉ PROSTŘEDÍ (převzato od tebe) ---
api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")
redis_host = os.environ.get("REDIS_HOST", "cache")

# --- PŘIPOJENÍ K DB ---
# Používáme Redis pro logování, jak je ve tvém kódu zvykem
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)

# Databáze otázek (původní logika kamarádky)
ALL_QUESTIONS = [
    {"id": 1, "q": "Kolik srdcí má chobotnice?", "opts": ["Jedno", "Dvě", "Tři", "Čtyři"], "ans": 2},
    {"id": 2, "q": "Který savec má nejhustší srst?", "opts": ["Lední medvěd", "Vydra mořská", "Činčila", "Bobr"], "ans": 1},
    {"id": 3, "q": "Věda studující ptáky?", "opts": ["Entomologie", "Ornitologie", "Ichtyologie", "Herpetologie"], "ans": 1},
    {"id": 4, "q": "Nejvyšší krevní tlak má?", "opts": ["Žirafa", "Velryba", "Slon", "Gepard"], "ans": 0},
    {"id": 5, "q": "Létá pozpátku?", "opts": ["Rorýs", "Albatros", "Kolibřík", "Sokol"], "ans": 2},
    {"id": 6, "q": "Barva kůže ledního medvěda?", "opts": ["Bílá", "Růžová", "Černá", "Šedá"], "ans": 2},
    {"id": 7, "q": "Počet žaludků krávy?", "opts": ["1", "2", "3", "4"], "ans": 3},
    {"id": 8, "q": "Nejrychlejší mořský tvor?", "opts": ["Plachetník", "Žralok", "Kosatka", "Tuňák"], "ans": 0},
    {"id": 9, "q": "Březost slona afrického?", "opts": ["12 měsíců", "18 měsíců", "22 měsíců", "24 měsíců"], "ans": 2},
    {"id": 10, "q": "Nejsilnější jed na světě?", "opts": ["Kobra", "Mamba", "Taipan", "Chřestýš"], "ans": 2},
    {"id": 11, "q": "Který pták má největší rozpětí křídel?", "opts": ["Orel", "Kondor", "Albatros", "Pelikán"], "ans": 2},
    {"id": 12, "q": "Které zvíře neumí skákat?", "opts": ["Slon", "Hroch", "Nosorožec", "Všechna uvedená"], "ans": 0}
]

@app.route('/')
def index():
    # Vybere 10 náhodných otázek pro každé načtení
    random_questions = random.sample(ALL_QUESTIONS, 10)
    return render_template('index.html', questions=random_questions)

@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.json
    user = data.get("user", "Anonym")
    score = int(data.get("score", 0))
    
    # Uložíme výsledek do Redisu pro logování (stejně jako tvůj log_pristupu)
    r.lpush('log_pristupu', f"Kvíz: {user} získal {score} bodů ({datetime.datetime.now().strftime('%H:%M:%S')})")
    
    # Tady by byla logika pro leaderboard, pokud ho chceš držet v paměti nebo v Redisu.
    # Pro jednoduchost zachovávám původní strukturu návratu, ale loguji to k tobě.
    return jsonify({"status": "ok", "user": user, "score": score})

@app.route('/ai', methods=['POST'])
def ai_comment():
    data = request.json
    score = data.get("score", 0)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gemma3:27b",
        "messages": [
            {"role": "system", "content": "Jsi vtipný zoolog."},
            {"role": "user", "content": f"Hráč získal {score}/10 v těžkém kvízu o zvířatech. Napiš mu jednu velmi krátkou vtipnou větu v češtině jako hodnocení."}
        ],
        "stream": False
    }

    try:
        # Oprava URL podle tvého vzoru (ořezání / a přidání /chat/completions)
        clean_url = f"{base_url.rstrip('/')}/chat/completions"
        res = requests.post(clean_url, headers=headers, json=payload, timeout=20, verify=False)
        
        if res.status_code == 200:
            ai_text = res.json()['choices'][0]['message']['content']
            r.lpush('log_pristupu', f"AI Zoolog odpověděl na skóre {score}")
            return jsonify({"ai_comment": ai_text})
        
        return jsonify({"ai_comment": "AI zoolog má teď pauzu na krmení (Chyba LLM)."}), 500
    except Exception as e:
        return jsonify({"ai_comment": f"Chyba: {str(e)}"}), 500

@app.route('/status')
def status():
    # Použijeme tvůj styl statusu, který ukazuje i logy z Redisu
    logs = r.lrange('log_pristupu', 0, 10) # posledních 10 záznamů
    return jsonify({
        "status": "running",
        "cas": datetime.datetime.now().isoformat(),
        "posledni_logy": logs
    })

if __name__ == '__main__':
    # Dynamický port podle tvého vzoru
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
