import os
import datetime
import random
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Konfigurace API (dodané údaje)
OPENAI_API_KEY = "sk-1k-KaViFjOIdiPvXYwBAQA"
OPENAI_BASE_URL = "https://kurim.ithope.eu/v1/chat/completions"
MY_PORT = int(os.getenv("APP_PORT", 8081))

leaderboard = []

# Databáze otázek
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
    leaderboard.append({"user": user, "score": score})
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(leaderboard[:10])

@app.route('/ai', methods=['POST'])
def ai_comment():
    data = request.json
    score = data.get("score", 0)
    
    # Nové volání přes OpenAI formát na URL v Kuřimi
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3.2:1b", # nebo jiný model, který na serveru běží
        "messages": [
            {"role": "system", "content": "Jsi vtipný zoolog."},
            {"role": "user", "content": f"Hráč získal {score}/10 v těžkém kvízu o zvířatech. Napiš mu jednu velmi krátkou vtipnou větu v češtině jako hodnocení."}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(OPENAI_BASE_URL, json=payload, headers=headers, timeout=10)
        result = response.json()
        ai_text = result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Chyba AI: {e}")
        ai_text = "AI zoolog má teď pauzu na krmení."

    return jsonify({"ai_comment": ai_text})

@app.route('/ping', methods=['GET'])
def ping():
    return "pong", 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "running",
        "autor": "Tvé Jméno",
        "cas": datetime.datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=MY_PORT)