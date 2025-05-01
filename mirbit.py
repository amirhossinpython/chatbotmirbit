import json
import re
import sqlite3
import requests
import wikipediaapi
from datetime import datetime


class MirbotAI:
    def __init__(self, dataset_path="mirbotai_dataset.json", db_path="mirbotai.db", wiki_lang='fa'):
        self.dataset_path = dataset_path
        self.db_path = db_path
        self.wiki = wikipediaapi.Wikipedia(language=wiki_lang, user_agent="MirbotAI/1.0 (contact: amirhossinpython03@gmail.com)")
        self.intents = self.load_intents()
        self.setup_database()
        self.sync_dataset_to_db()

    def load_intents(self):
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_intents(self):
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            json.dump(self.intents, f, ensure_ascii=False, indent=4)

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                timestamp TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS intents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent TEXT,
                pattern TEXT,
                answer TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def sync_dataset_to_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for intent in self.intents:
            for pattern in intent["patterns"]:
                c.execute('''
                    SELECT 1 FROM intents WHERE intent = ? AND pattern = ? AND answer = ?
                ''', (intent["intent"], pattern, intent["answer"]))
                if not c.fetchone():
                    c.execute('''
                        INSERT INTO intents (intent, pattern, answer) VALUES (?, ?, ?)
                    ''', (intent["intent"], pattern, intent["answer"]))

        conn.commit()
        conn.close()

    def save_history(self, question, answer):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO history (question, answer, timestamp) VALUES (?, ?, ?)",
                  (question, answer, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_last_question(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT question FROM history ORDER BY id DESC LIMIT 1")
        result = c.fetchone()
        conn.close()
        return result[0] if result else "هیچ سوال قبلی ثبت نشده است."

    def prepare_pattern(self, pattern):
        pattern = re.escape(pattern).replace(r"\ ", r"\s*")
        return rf"\b{pattern}\b"

    def match_intent(self, user_input):
        for intent in self.intents:
            for pattern in intent["patterns"]:
                if re.search(self.prepare_pattern(pattern), user_input, re.IGNORECASE):
                    if intent["answer"] == "<HISTORY>":
                        return self.get_last_question()
                    return intent["answer"]
        return None

    def search_wikipedia(self, query, full=False):
        page = self.wiki.page(query)
        if page.exists():
            return page.text if full else f"**{page.title}**\n\n{page.summary[:1000]}..."
        return None

    def get_response_from_api(self, user_input):
        try:
            url = "https://api.api-code.ir/gpt-4/"
            response = requests.get(url, params={"text": user_input})
            response.raise_for_status()
            return response.json()['result']
        except Exception as e:
            return f"خطا در ارتباط با وب‌سرویس: {e}"

    def respond(self, user_input):
        response = self.match_intent(user_input)
        if not response:
            response = self.search_wikipedia(user_input)
        if not response:
            response = self.get_response_from_api(user_input)

        self.save_history(user_input, response)
        return response

    def add_intent(self, intent, patterns, answer):
        self.intents.append({
            "intent": intent,
            "patterns": patterns,
            "answer": answer
        })
        self.save_intents()
        self.sync_dataset_to_db()
        






        
    
    

