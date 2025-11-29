import logging
import requests
import re
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- CONFIGURAZIONE ---
# Il token verrà preso dalle variabili d'ambiente di Render
TOKEN = os.getenv("TOKEN_BOT")

# --- LISTA AULE CON PRESE ---
# AULE_CON_PRESE = {
#    "R1", "R2", "R3", "R4", 
 #   "12A", "14A", "15A", "16A",
  #  "1I", "2I", "3I", "4I", "5I",
   # "LAIB1", "LAIB2", "Sala Tesisti",
    #"Agorà", "Aquarium"
#}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- TRUCCO PER RENDER (Finto Server Web) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Il Bot e' vivo e vegeto!")

def start_fake_server():
    # Render ci dice su quale porta ascoltare tramite la variabile PORT
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🌍 Finto server web avviato sulla porta {port}")
    server.serve_forever()
# ------------------------------------------

def formatta_aule_con_prese(testo_grezzo):
    lista_aule = testo_grezzo.split(',')
    lista_formattata = []
    for aula in lista_aule:
        nome_pulito = aula.strip()
        if nome_pulito in AULE_CON_PRESE:
            lista_formattata.append(f"<b>{nome_pulito}</b>🔌")
        else:
            lista_formattata.append(nome_pulito)
    return ", ".join(lista_formattata)

def ottieni_aule_swas():
    url = "https://www.swas.polito.it/dotnet/orari_lezione_pub/ricercaaulelibereperfasceorarie.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return "⚠️ Errore di connessione al sito Polito."

        soup = BeautifulSoup(response.text, 'html.parser')
        messaggio = []
        messaggio.append("🎓 **AULE LIBERE POLITO** 🎓")
        messaggio.append("*(Le aule con 🔌 hanno le prese)*\n")

        aule_spans = soup.find_all('span', id=re.compile("lbl_AuleLibere"))

        if not aule_spans:
            return "❌ Non ho trovato la tabella. Il sito potrebbe essere cambiato."

        count = 0
        for span_aula in aule_spans:
            testo_aule = span_aula.text.strip()
            if not testo_aule:
                continue

            riga_padre = span_aula.find_parent('tr')
            orario = "??"
            if riga_padre:
                celle = riga_padre.find_all('td')
                if celle:
                    orario = celle[0].text.strip()

            aule_formattate = formatta_aule_con_prese(testo_aule)
            messaggio.append(f"🕒 {orario}")
            messaggio.append(f"🏫 {aule_formattate}") 
            messaggio.append("───────────────")
            count += 1

        if count == 0:
            return "Nessuna aula libera trovata al momento."
        return "\n".join(messaggio)
    except Exception as e:
        return f"❌ Errore tecnico: {e}"

async def aule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Controllo SWAS e cerco le prese... ⏳")
    risultato = ottieni_aule_swas()
    if len(risultato) > 4000:
        await update.message.reply_text(risultato[:4000] + "\n...(tagliato)...", parse_mode='HTML')
    else:
        await update.message.reply_text(risultato, parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Scrivi /aule per vedere dove studiare.")

if __name__ == '__main__':
    if not TOKEN:
        print("⚠️ Errore: TOKEN_BOT mancante!")
        exit()

    # --- AVVIO DEL FINTO SERVER IN BACKGROUND ---
    # Questo thread serve solo a tenere contento Render
    t = threading.Thread(target=start_fake_server)
    t.daemon = True
    t.start()
    # --------------------------------------------

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('aule', aule))
    
    print("🤖 Bot avviato!")
    application.run_polling()
