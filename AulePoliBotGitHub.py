import logging
import requests
import re
import os
import json # <--- Nuova libreria per leggere il file
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- CONFIGURAZIONE ---
TOKEN = os.getenv("TOKEN_BOT")

# --- CARICAMENTO LISTA PRESE DA FILE JSON ---
# Invece di scriverle a mano, le leggiamo dal file generato dal crawler
try:
    with open('aule_prese.json', 'r') as f:
        # Carichiamo la lista e la trasformiamo in un 'set' (più veloce per le ricerche)
        lista_json = json.load(f)
        AULE_CON_PRESE = set(lista_json)
        print(f"✅ Caricate {len(AULE_CON_PRESE)} aule con prese dal file JSON.")
except Exception as e:
    print(f"⚠️ Attenzione: Non riesco a leggere 'aule_prese.json'. Errore: {e}")
    print("Uso una lista vuota per ora.")
    AULE_CON_PRESE = set()
# ---------------------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- TRUCCO PER RENDER (Keep-Alive) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Polito Online")

def start_fake_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()
# ---------------------------------------

def formatta_aule_con_prese(testo_grezzo):
    """
    Legge '1, 10, R1' e mette la spina se l'aula è nel JSON
    """
    lista_aule = testo_grezzo.split(',')
    lista_formattata = []
    
    for aula in lista_aule:
        nome_pulito = aula.strip()
        
        # Pulizia extra: a volte swas scrive "Aula 1", nel json abbiamo "Aula 1"
        # Ma a volte swas scrive "1". Dobbiamo gestire i casi.
        # Controllo semplice: se il nome esatto è nella lista
        is_presenza = False
        
        if nome_pulito in AULE_CON_PRESE:
            is_presenza = True
        # Controllo extra: se nel json c'è "Aula 1" e swas dice "1", proviamo a combinare
        elif f"Aula {nome_pulito}" in AULE_CON_PRESE:
            is_presenza = True
            
        if is_presenza:
            lista_formattata.append(f"<b>{nome_pulito}</b>🔌")
        else:
            lista_formattata.append(nome_pulito)
            
    return ", ".join(lista_formattata)

def ottieni_aule_swas(solo_prese=False):
    url = "https://www.swas.polito.it/dotnet/orari_lezione_pub/ricercaaulelibereperfasceorarie.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return "⚠️ Errore sito Polito."

        soup = BeautifulSoup(response.text, 'html.parser')
        messaggio = []
        messaggio.append("🎓 **AULE LIBERE POLITO** 🎓")
        messaggio.append(f"*(Database prese aggiornato: {len(AULE_CON_PRESE)} aule)*\n")

        aule_spans = soup.find_all('span', id=re.compile("lbl_AuleLibere"))

        if not aule_spans:
            return "❌ Tabella orari non trovata."

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
            return "Nessuna aula libera trovata."
        return "\n".join(messaggio)

    except Exception as e:
        return f"❌ Errore: {e}"


# --- I COMANDI DEL BOT ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Ciao {user_name}, controllo il sito SWAS per te... ⏳")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    testo_help = (
        "🤖 <b>GUIDA AI COMANDI</b> 🤖\n\n"
        "🔹 <b>/auleAll</b> (oppure <b>/aule</b>)\n"
        "Ti mostra l'elenco completo di tutte le aule libere in questo momento. "
        "Le aule segnate con 🔌 hanno le prese elettriche disponibili.\n\n"
        "🔹 <b>/prese</b>\n"
        "Filtra la lista e ti mostra <u>SOLO</u> le aule libere che hanno le prese. "
        "Usalo quando hai il PC scarico!😉\n\n"
        "🔹 <b>/help</b>\n"
        "Mostra questo messaggio di aiuto.🆘\n\n"
        "<i>Presto arriveranno nuove funzioni... stay tuned!</i> 🚀"
    )
    await update.message.reply_text(testo_help, parse_mode='HTML')


async def aule_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Cerco tutte le aule libere...")
    risultato = ottieni_aule_swas(solo_prese=False)
    # Invio sicuro (spezza se troppo lungo)
    if len(risultato) > 4000:
        await update.message.reply_text(risultato[:4000] + "...", parse_mode='HTML')
    else:
        await update.message.reply_text(risultato, parse_mode='HTML')


async def prese(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔌 Filtro solo le aule con prese...")
    risultato = ottieni_aule_swas(solo_prese=True)
    if len(risultato) > 4000:
        await update.message.reply_text(risultato[:4000] + "...", parse_mode='HTML')
    else:
        await update.message.reply_text(risultato, parse_mode='HTML')






if __name__ == '__main__':
    if not TOKEN:
        print("⚠️ Token mancante")
        exit()

    t = threading.Thread(target=start_fake_server)
    t.daemon = True
    t.start()

    application = ApplicationBuilder().token(TOKEN).build()

    # Registrazione nuovi comandi
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('auleall', aule_all))
    application.add_handler(CommandHandler('prese', prese))
    
    
    # Mantengo anche il vecchio /aule come alias per /auleAll (comodo per abitudine)
    application.add_handler(CommandHandler('aule', aule_all))
    
    print("🤖 Bot avviato con supporto JSON!")
    application.run_polling()

