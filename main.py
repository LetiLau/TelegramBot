###############################
# main.py (Il capo): Gestisce Telegram, i comandi e coordina gli altri due.
###############################

import os
import time
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- IMPORTIAMO I NOSTRI FILE ---
import utils   # Importa utils.py
import scraper # Importa scraper.py

# --- CONFIGURAZIONE ---
TOKEN = os.getenv("TOKEN_BOT")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- COMANDI BOT ---

async def aule_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Scarico tutte le aule...")
    dati = scraper.scarica_dati_swas() # Chiamo lo scraper
    
    if not dati:
        await update.message.reply_text("❌ Errore sito Polito.")
        return

    messaggio = ["🎓 **TUTTE LE AULE LIBERE** 🎓\n"]
    
    for orario, lista_aule in dati.items():
        # Uso la funzione di utils per mettere le icone
        nomi_belli = [utils.formatta_nome(a) for a in lista_aule]
        testo = ", ".join(nomi_belli)
        
        messaggio.append(f"🕒 {orario}")
        messaggio.append(f"🏫 {testo}")
        messaggio.append("───────────────")
        
    await invia_lungo(update, "\n".join(messaggio))

async def prese(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔌 Filtro solo prese...")
    dati = scraper.scarica_dati_swas()
    if not dati: return

    messaggio = ["🔌 **SOLO CON PRESE** 🔌\n"]
    
    for orario, lista_aule in dati.items():
        # Filtro: tengo solo se utils dice che ha la presa
        lista_prese = [f"<b>{a}</b>" for a in lista_aule if utils.controlla_presa(a)]
        
        if lista_prese:
            messaggio.append(f"🕒 {orario}")
            messaggio.append(f"🏫 {', '.join(lista_prese)}")
            messaggio.append("───────────────")
            
    await invia_lungo(update, "\n".join(messaggio))

async def maratona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏃‍♂️ Calcolo Maratona Studio...")
    dati = scraper.scarica_dati_swas()
    
    if not dati or len(dati) < 2:
        await update.message.reply_text("⚠️ Troppe poche fasce orarie per una maratona oggi.")
        return

    orari = list(dati.keys())
    messaggio = ["🏆 **MARATONA STUDIO** 🏆\n"]
    trovato = False

    for i in range(len(orari) - 1):
        ora_curr = orari[i]
        ora_next = orari[i+1]
        
        # Intersezione matematica dei due elenchi
        comuni = list(set(dati[ora_curr]).intersection(set(dati[ora_next])))
        comuni.sort()
        
        if comuni:
            trovato = True
            nomi = [utils.formatta_nome(a) for a in comuni]
            start = ora_curr.split('-')[0]
            end = ora_next.split('-')[1]
            
            messaggio.append(f"🔥 **{start} -> {end}**")
            messaggio.append(f"Aule: {', '.join(nomi)}")
            messaggio.append("───────────────")
    
    if not trovato: messaggio.append("😢 Nessuna maratona possibile oggi.")
    await invia_lungo(update, "\n".join(messaggio))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    testo = (
        "🤖 <b>GUIDA AI COMANDI</b> 🤖\n\n"
        "🔹 <b>/auleAll</b> (oppure <b>/aule</b>)\n"
        "Ti mostra l'elenco completo di tutte le aule libere in questo momento. "
        "Le aule segnate con 🔌 hanno le prese elettriche disponibili.\n\n"
        "🔹 <b>/prese</b>\n"
        "Filtra la lista e ti mostra <u>SOLO</u> le aule libere che hanno le prese a tua disposizione. "
        "Usalo quando hai il PC scarico!😉\n\n"
        "🔹 <b>/maratona</b>\n"
        "Mostra le aule che hanno liberi due turni consecutivi (tot. 3h)"
        "🔹 <b>/help</b>\n"
        "Mostra questo messaggio di aiuto🆘.\n\n"
        "<i>Presto arriveranno nuove funzioni... stay tuned!</i> 🚀"
    )
    await update.message.reply_text(testo, parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Ciao {user_name}! Ecco tutti i comandi disponibili.")

# Funzione helper per mandare messaggi lunghi
async def invia_lungo(update, testo):
    if len(testo) > 4000:
        for x in range(0, len(testo), 4000):
            await update.message.reply_text(testo[x:x+4000], parse_mode='HTML')
    else:
        await update.message.reply_text(testo, parse_mode='HTML')

# --- AVVIO ---
if __name__ == '__main__':
    print("💤 Pausa avvio...")
    time.sleep(5)
    
    if not TOKEN: exit()

    # Avvio i servizi di utilità
    utils.carica_prese()          # Carica il JSON
    utils.avvia_server_background() # Avvia il finto server per Render

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('auleall', aule_all))
    app.add_handler(CommandHandler('aule', aule_all))
    app.add_handler(CommandHandler('prese', prese))
    app.add_handler(CommandHandler('maratona', maratona))
    
    print("🤖 Bot Avviato!")
    app.run_polling()
