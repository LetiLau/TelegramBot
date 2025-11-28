import logging
import requests
import re
import os
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 1. CONFIGURAZIONE LOGGING
# Serve per leggere eventuali errori nel terminale
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 2. LA FUNZIONE "CERVELLO" (Scraping SWAS)
def ottieni_aule_swas():
    url = "https://www.swas.polito.it/dotnet/orari_lezione_pub/ricercaaulelibereperfasceorarie.aspx"
    
    # Ci fingiamo un browser vero
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return "⚠️ Errore di connessione al sito Polito."

        soup = BeautifulSoup(response.text, 'html.parser')
        messaggio = []
        
        # Aggiungiamo un'intestazione
        messaggio.append("🎓 **AULE LIBERE POLITO (Oggi)** 🎓\n")

        # Cerchiamo gli span che contengono "lbl_AuleLibere" nell'ID
        aule_spans = soup.find_all('span', id=re.compile("lbl_AuleLibere"))

        if not aule_spans:
            return "❌ Non ho trovato la tabella. Il sito potrebbe essere cambiato."

        count = 0
        for span_aula in aule_spans:
            # Testo delle aule
            testo_aule = span_aula.text.strip()
            if not testo_aule:
                continue

            # Cerchiamo l'orario risalendo alla riga (tr) e poi alla prima cella (td)
            riga_padre = span_aula.find_parent('tr')
            orario = "??"
            if riga_padre:
                celle = riga_padre.find_all('td')
                if celle:
                    orario = celle[0].text.strip()

            # Formattazione del messaggio
            messaggio.append(f"🕒 *{orario}*")
            messaggio.append(f"🏫 `{testo_aule}`") # Usa il font 'code' per copiare meglio
            messaggio.append("───────────────")
            count += 1

        if count == 0:
            return "Nessuna aula libera trovata al momento."

        return "\n".join(messaggio)

    except Exception as e:
        return f"❌ Errore tecnico nel codice: {e}"

# 3. LA FUNZIONE "VOCE" (Risposta Telegram)
async def aule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Ciao {user_name}, controllo il sito SWAS per te... ⏳")
    
    # Chiama la funzione di scraping
    testo_risposta = ottieni_aule_swas()
    
    # Telegram non accetta messaggi più lunghi di 4096 caratteri.
    # Se la lista è lunghissima, la spezziamo (controllo di sicurezza base)
    if len(testo_risposta) > 4000:
        await update.message.reply_text(testo_risposta[:4000] + "\n... (messaggio tagliato per limite lunghezza)", parse_mode='Markdown')
    else:
        await update.message.reply_text(testo_risposta, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Scrivi /aule per vedere dove puoi studiare oggi.")

# 4. IL MOTORE PRINCIPALE
if __name__ == '__main__':
    # SCRIVI QUESTO: Dice al bot di cercarlo nelle impostazioni del server
    TOKEN = os.getenv("TOKEN_BOT") 
    
    if not TOKEN:
        print("⚠️ Errore: Manca il TOKEN_BOT nelle variabili d'ambiente!")
        exit()
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('aule', aule))
    
    print("🤖 Il Bot è acceso e in ascolto!")
    application.run_polling()