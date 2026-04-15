import os
import datetime
import random
import requests
import urllib3
from flask import Flask, request, jsonify, render_template, load_dotenv

# --- KONFIGURACE (Přesně podle tvého vzoru) ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# load_dotenv() # Odkomentuj, pokud používáš .env soubor


# --- PROMĚNNÉ PROSTŘEDÍ ---
# Tyto proměnné zajistí, že se aplikace spojí s AI serverem v Kuřimi
api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL", "https://kurim.ithope.eu/v1")

# --- DATA KVÍZU (Logika kamarádky) ---
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

# --- ROUTY ---

@app.route('/')
def index():
    # Vybere 10 náhodných otázek pro hru
    random_questions = random.sample(ALL_QUESTIONS, 10)
    # Zobrazí index.html (rozhraní tvé aplikace)
    return render_template('index.html', questions=random_questions)

@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.json
    user = data.get("user", "Anonym")
    score = int(data.get("score", 0))
    return jsonify({"status": "success", "user": user, "score": score})

# --- AI LOGIKA (Implementace tvého ai_advisor stylu) ---
@app.route('/ai', methods=['POST'])
def ai_comment():
    data = request.json
    score = data.get("score", 0)
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    payload = {
        "model": "gemma3:27b", 
        "messages": [
            {"role": "system", "content": "Jsi vtipný zoolog."},
            {"role": "user", "content": f"Hráč získal {score}/10 v kvízu o zvířatech. Napiš mu jednu velmi krátkou vtipnou větu v češtině jako hodnocení."}
        ], 
        "stream": False
    }

    try:
        # Tvá metoda čištění URL
        clean_url = f"{base_url.rstrip('/')}/chat/completions"
        res = requests.post(clean_url, headers=headers, json=payload, timeout=20, verify=False)
        
        if res.status_code == 200:
            msg = res.json()['choices'][0]['message']['content']
            return jsonify({"ai_comment": msg})
        
        return jsonify({"error": f"Chyba LLM: {res.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def status():
    # Jednoduchý status pro kontrolu běhu na tvé subdoméně
    return jsonify({
        "app": "Zvířecí Kvíz",
        "url": "https://sarka-kasikova.kurim.ithope.eu/",
        "status": "online",
        "timestamp": datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Spuštění na portu, který definuje tvé prostředí (standardně 5000)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
