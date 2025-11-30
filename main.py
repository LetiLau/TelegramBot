###############################
# main.py (Il capo): Gestisce Telegram, i comandi e coordina gli altri due.
###############################
import os
import time
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import utils
import scraper

TOKEN = os.getenv("TOKEN_BOT")
ADMIN_ID = os.getenv("ADMIN_ID") 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- DISCLAIMER STANDARD ---
DISCLAIMER = "\n⚠️ <i>La posizione sulla mappa indica l'ingresso del padiglione.\nPer l'ubicazione esatta, controlla i cartelli o l'app ufficiale Polito.</i>"

# --- COMANDI ---

async def aule_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Scarico tutte le aule...")
    dati = scraper.scarica_dati_swas()
    
    if not dati:
        await update.message.reply_text("❌ Errore sito Polito.")
        return

    messaggio = ["🎓 **TUTTE LE AULE LIBERE** 🎓\n(Clicca sul nome per la mappa)\n"]
    
    for orario, lista_aule in dati.items():
        nomi_belli = [utils.formatta_nome(a) for a in lista_aule]
        testo = ", ".join(nomi_belli)
        messaggio.append(f"🕒 {orario}\n🏫 {testo}\n───────────────")
    
    # Aggiungiamo il disclaimer alla fine
    messaggio.append(DISCLAIMER)
        
    await invia_lungo(update, "\n".join(messaggio))

async def prese(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔌 Filtro solo prese...")
    dati = scraper.scarica_dati_swas()
    if not dati: return

    messaggio = ["🔌 **SOLO CON PRESE** 🔌\n(Clicca sul nome per la mappa)\n"]
    
    for orario, lista_aule in dati.items():
        lista_prese = [utils.formatta_nome(a) for a in lista_aule if utils.controlla_presa(a)]
        
        if lista_prese:
            messaggio.append(f"🕒 {orario}\n🏫 {', '.join(lista_prese)}\n───────────────")
            
    messaggio.append(DISCLAIMER)
    await invia_lungo(update, "\n".join(messaggio))

async def maratona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏃‍♂️ Calcolo Maratona Studio...")
    dati = scraper.scarica_dati_swas()
    
    if not dati or len(dati) < 2:
        await update.message.reply_text("⚠️ Troppe poche fasce orarie oggi.")
        return

    orari = list(dati.keys())
    messaggio = ["🏆 **MARATONA STUDIO** 🏆\n"]
    trovato = False

    for i in range(len(orari) - 1):
        ora_curr = orari[i]
        ora_next = orari[i+1]
        comuni = list(set(dati[ora_curr]).intersection(set(dati[ora_next])))
        comuni.sort()
        
        if comuni:
            trovato = True
            nomi = [utils.formatta_nome(a) for a in comuni]
            start = ora_curr.split('-')[0]
            end = ora_next.split('-')[1]
            messaggio.append(f"🔥 **{start} -> {end}**\n📍 {', '.join(nomi)}\n───────────────")
    
    if not trovato: 
        messaggio.append("😢 Nessuna maratona possibile oggi.")
    else:
        messaggio.append(DISCLAIMER)
        
    await invia_lungo(update, "\n".join(messaggio))

async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messaggio_utente = " ".join(context.args)
    if not messaggio_utente:
        await update.message.reply_text("⚠️ Scrivi il tuo messaggio dopo il comando.", parse_mode='HTML')
        return

    if not ADMIN_ID:
        await update.message.reply_text("⚠️ Funzione non configurata.")
        return

    username = update.effective_user.username or update.effective_user.first_name
    report = f"💡 <b>NUOVO SUGGERIMENTO</b>\nUtente: @{username}\n\n<i>{messaggio_utente}</i>"
    
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=report, parse_mode='HTML')
        await update.message.reply_text("✅ Inviato allo sviluppatore!")
    except Exception as e:
        await update.message.reply_text("❌ Errore invio.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    testo = (
        "🤖 <b>GUIDA AI COMANDI</b> 🤖\n\n"
        "🔹 <b>/start</b>\n"
        "Avvia il bot dall'inizio\n\n"
        "🔹 <b>/help</b>\n"
        "Mostra questo messaggio di aiuto🆘.\n\n"
        "🔹 <b>/suggest ..... </b>\n"
        "Invia un suggerimento al mio admin 💡\n\n"
        "🔹 <b>/auleAll</b> (oppure <b>/aule</b> oppure <b>/auleall</b>)\n"
        "Ti mostra l'elenco completo di tutte le aule libere in questo momento. "
        "Le aule segnate con 🔌 hanno le prese elettriche disponibili.\n\n"
        "🔹 <b>/prese</b>\n"
        "Filtra la lista e ti mostra <u>SOLO</u> le aule libere che hanno le prese a tua disposizione. "
        "Usalo quando hai il PC scarico!😉\n\n"
        "🔹 <b>/maratona</b>\n"
        "Mostra le aule che hanno liberi due turni consecutivi (tot. 3h)"
        
       
        "<i>Presto arriveranno nuove funzioni... stay tuned!</i> 🚀"
    )
    await update.message.reply_text(testo, parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Ciao {user_name}! Ecco tutti i comandi disponibili ⬇️")

async def invia_lungo(update, testo):
    SEPARATORE = "───────────────"
    blocchi = testo.split(SEPARATORE)
    chunk = ""
    for blocco in blocchi:
        if not blocco.strip(): continue
        pezzo_completo = blocco.strip() + "\n" + SEPARATORE + "\n"
        if len(chunk) + len(pezzo_completo) > 4000:
            await update.message.reply_text(chunk, parse_mode='HTML')
            chunk = ""
        chunk += pezzo_completo
    if chunk:
        await update.message.reply_text(chunk, parse_mode='HTML')

if __name__ == '__main__':
    print("💤 Pausa avvio...")
    time.sleep(5)
    
    if not TOKEN: exit()

    utils.carica_prese()
    utils.avvia_server_background()

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('auleAll', aule_all))
    app.add_handler(CommandHandler('aule', aule_all))
    app.add_handler(CommandHandler('prese', prese))
    app.add_handler(CommandHandler('maratona', maratona))
    app.add_handler(CommandHandler('suggest', suggest))
    
    print("🤖 Bot Avviato!")
    app.run_polling()
