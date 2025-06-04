from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "¡Estoy vivo!"

def run():
    port = int(os.environ.get("PORT", 10000))  # Render espera este puerto
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
