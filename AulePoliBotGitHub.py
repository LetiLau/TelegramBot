import logging
import requests
import re
import os
import json
# import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- CONFIGURAZIONE ---
TOKEN = os.getenv("TOKEN_BOT")

# --- CARICAMENTO LISTA PRESE ---
try:
    with open('aule_prese.json', 'r') as f:
        lista_json = json.load(f)
        AULE_CON_PRESE = set(lista_json)
        print(f"✅ Database prese caricato: {len(AULE_CON_PRESE)} aule.")
except Exception as e:
    print(f"⚠️ Errore caricamento JSON: {e}")
    AULE_CON_PRESE = set()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- FINTO SERVER PER RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Polito Online")

def start_fake_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- LOGICA FILTRO E FORMATTAZIONE ---
def elabora_testo_aule(testo_grezzo, solo_prese=False):
    lista_aule = testo_grezzo.split(',')
    lista_finale = []
    
    for aula in lista_aule:
        nome_pulito = aula.strip()
        
        # Check se ha la presa (controlla sia "1" che "Aula 1")
        ha_presa = (nome_pulito in AULE_CON_PRESE) or (f"Aula {nome_pulito}" in AULE_CON_PRESE)
        
        if solo_prese:
            # CASO 1: Voglio SOLO le prese
            if ha_presa:
                lista_finale.append(f"<b>{nome_pulito}</b>")
            # Se non ha la presa, non faccio nulla (la ignoro)
        else:
            # CASO 2: Voglio tutto
            if ha_presa:
                lista_finale.append(f"<b>{nome_pulito}</b>🔌")
            else:
                lista_finale.append(nome_pulito)
            
    if not lista_finale:
        return ""
        
    return ", ".join(lista_finale)

# --- SCRAPING SWAS ---
def ottieni_aule_swas(solo_prese=False):
    url = "https://www.swas.polito.it/dotnet/orari_lezione_pub/ricercaaulelibereperfasceorarie.aspx"
    headers = { "User-Agent": "Mozilla/5.0" }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200: 
            return "⚠️ Errore sito Polito."

        soup = BeautifulSoup(response.text, 'html.parser')
        messaggio = []
        
        if solo_prese:
            messaggio.append("🔌 **SOLO AULE CON PRESE** 🔌")
        else:
            messaggio.append("🎓 **TUTTE LE AULE LIBERE** 🎓")
            messaggio.append("*(Le aule con 🔌 hanno le prese)*")
            
        messaggio.append("")

        aule_spans = soup.find_all('span', id=re.compile("lbl_AuleLibere"))

        if not aule_spans: 
            return "❌ Nessuna tabella orari trovata."

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

            # --- LA RIGA CRUCIALE ERA QUI SOTTO ---
            # Passiamo il parametro solo_prese anche alla funzione che pulisce il testo
            aule_stringa = elabora_testo_aule(testo_aule, solo_prese=solo_prese)
            
            # Se dopo il filtro la stringa è vuota, saltiamo la fascia oraria
            if not aule_stringa:
                continue

            messaggio.append(f"🕒 {orario}")
            messaggio.append(f"🏫 {aule_stringa}") 
            messaggio.append("───────────────")
            count += 1

        if count == 0: 
            return "Nessuna aula trovata con questi criteri."
            
        return "\n".join(messaggio)

    except Exception as e:
        return f"❌ Errore tecnico: {e}"

# --- HANDLERS TELEGRAM ---

async def aule_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Cerco tutte le aule libere...")
    risultato = ottieni_aule_swas(solo_prese=False)
    if len(risultato) > 4000:
        await update.message.reply_text(risultato[:4000] + "...", parse_mode='HTML')
    else:
        await update.message.reply_text(risultato, parse_mode='HTML')

async def prese(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔌 Filtro solo le aule con prese...")
    # Qui diciamo True, che viene passato a ottieni_aule, che lo passa a elabora_testo
    risultato = ottieni_aule_swas(solo_prese=True)
    if len(risultato) > 4000:
        await update.message.reply_text(risultato[:4000] + "...", parse_mode='HTML')
    else:
        await update.message.reply_text(risultato, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    testo = (
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
    await update.message.reply_text(testo, parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Scrivi /help per vedere i comandi.")

if __name__ == '__main__':
    # Pausa tattica per evitare conflitti su Render al riavvio
    # print("💤 Pausa avvio anti-conflitto...")
    # time.sleep(5)

    if not TOKEN:
        print("⚠️ TOKEN MANCANTE")
        exit()

    t = threading.Thread(target=start_fake_server)
    t.daemon = True
    t.start()

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('auleall', aule_all))
    application.add_handler(CommandHandler('aule', aule_all))
    application.add_handler(CommandHandler('prese', prese))
    application.add_handler(CommandHandler('help', help_command))
    
    print("🤖 Bot avviato!")
    application.run_polling()
