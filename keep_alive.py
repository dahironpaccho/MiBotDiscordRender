from flask import Flask
from threading import Thread
import os # ¡Añade esta línea!

app = Flask('')

@app.route('/')
def home():
    return "Bot está funcionando!"

def run():
  # Obtiene el puerto de la variable de entorno 'PORT' de Render, si no existe, usa 8080 (por si corres localmente)
  # Render usa el puerto 10000 por defecto.
  port = int(os.environ.get("PORT", 8080)) # ¡Modifica esta línea para usar la variable de entorno PORT!
  app.run(host='0.0.0.0',port=port) # ¡Modifica esta línea para usar el puerto dinámico!

def keep_alive():
    t = Thread(target=run)
    t.start()
