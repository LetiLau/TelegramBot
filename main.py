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

# --- 🎨 SEZIONE ESTETICA (MODIFICA QUI) 🎨 ---

# Linea che divide le fasce orarie (copia-incolla caratteri speciali se vuoi)
SEPARATORE = "───────────────"

# Print avvio per Render
AVVIO = "🤖 Bot Avviato!"

# Intestazioni dei messaggi
HEADER_AULE_ALL = "🎓 ** TUTTE LE AULE LIBERE ** 🎓\n"
HEADER_PRESE    = "🔌 ** SOLO CON PRESE ** 🔌\n"
HEADER_MARATONA = "🏆 ** MARATONA STUDIO ** 🏆\n(Aule libere per più turni consecutivi)\n"

# Disclaimer finale
DISCLAIMER = "\n⚠️ <i>La posizione sulla mappa indica l'ingresso del padiglione dell'aula o la zona di riferimento più vicina alla sua effettiva posizione.\nPer l'ubicazione esatta, controlla i cartelli o l'app ufficiale PoliTO.</i>"

# Icone varie
ICON_OROLOGIO = "🕒"
ICON_SCUOLA   = "🏫📍(Clicca sull'aula per ottenere la posizione)"
ICON_FUOCO    = "🔥"
ICON_PIN      = "" #NON RIMUOVERE, manderebbe in tilt il messaggio

# ---------------------------------------------

# --- COMANDI ---

async def aule_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Scarico tutte le aule...")
    dati = scraper.scarica_dati_swas()
    
    if not dati:
        await update.message.reply_text("❌ Errore sito Polito.")
        return

    messaggio = [HEADER_AULE_ALL]
    
    for orario, lista_aule in dati.items():
        nomi_belli = [utils.formatta_nome(a) for a in lista_aule]
        testo = ", ".join(nomi_belli)
        
        # Costruzione blocco usando le variabili estetiche
        blocco = f"{ICON_OROLOGIO} {orario}\n{ICON_SCUOLA} {testo}\n{SEPARATORE}"
        messaggio.append(blocco)
    
    messaggio.append(DISCLAIMER)
    await invia_lungo(update, "\n".join(messaggio))

async def prese(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔌 Filtro solo prese...")
    dati = scraper.scarica_dati_swas()
    if not dati: return

    messaggio = [HEADER_PRESE]
    
    for orario, lista_aule in dati.items():
        # mostra_icona=False perché siamo già nel menu prese
        lista_prese = [utils.formatta_nome(a, mostra_icona=False) for a in lista_aule if utils.controlla_presa(a)]
        
        if lista_prese:
            blocco = f"{ICON_OROLOGIO} {orario}\n{ICON_SCUOLA} {', '.join(lista_prese)}\n{SEPARATORE}"
            messaggio.append(blocco)
            
    messaggio.append(DISCLAIMER)
    await invia_lungo(update, "\n".join(messaggio))

async def maratona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏃‍♂️ Calcolo Maratona Studio...")
    dati = scraper.scarica_dati_swas()
    
    if not dati or len(dati) < 2:
        await update.message.reply_text("⚠️ Troppe poche fasce orarie oggi.")
        return

    orari = list(dati.keys())
    messaggio = [HEADER_MARATONA]
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
            
            blocco = f"{ICON_FUOCO} **{start} -> {end}**\n{ICON_PIN} {', '.join(nomi)}\n{SEPARATORE}"
            messaggio.append(blocco)
    
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
    # Puoi personalizzare anche questo testo qui
    testo = (
        "🤖 <b>GUIDA AI COMANDI</b> 🤖\n\n"
        "🔹 <b>/start</b>\n"
        "Avvia il bot dall'inizio\n\n"
        "🔹 <b>/help</b>\n"
        "Mostra questo messaggio di aiuto🆘.\n\n"
        "🔹 <b>/suggest 'your message' </b>\n"
        "Invia un suggerimento al mio admin 💡\n\n"
        "🔹 <b>/auleAll</b> (oppure <b>/aule</b> oppure <b>/auleall</b>)\n"
        "Ti mostra l'elenco completo di tutte le aule libere in questo momento. "
        "Le aule segnate con 🔌 hanno le prese elettriche disponibili.\n\n"
        "🔹 <b>/prese</b>\n"
        "Filtra la lista e ti mostra <u>SOLO</u> le aule libere che hanno le prese a tua disposizione. "
        "Usalo quando hai il PC scarico!😉\n\n"
        "🔹 <b>/maratona</b>\n"
        "Mostra le aule che hanno liberi due turni consecutivi (tot. 3h)📚\n\n"
        "<i>Presto arriveranno nuove funzioni... stay tuned!</i> 🚀"
    )
    await update.message.reply_text(testo, parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Usa /help per info.")


# --- UTILS MESSAGGI ---
async def invia_lungo(update, testo):
    # Ora usa la variabile globale definita in alto!
    # Non devi più cambiarla qui dentro manualmente.
    blocchi = testo.split(SEPARATORE)
    chunk = ""
    
    for blocco in blocchi:
        if not blocco.strip(): continue
        
        pezzo_completo = blocco.strip() + "\n" + SEPARATORE + "\n"
        
        # CASO MOSTRUOSO (Domenica)
        if len(pezzo_completo) > 4000:
            if chunk:
                await update.message.reply_text(chunk, parse_mode='HTML', disable_web_page_preview=True)
                chunk = ""
            
            righe = pezzo_completo.split('\n')
            intestazione = righe[0] + "\n"
            corpo_aule = "\n".join(righe[1:-2]) 
            lista_aule = corpo_aule.split(',')
            
            # Qui usiamo l'icona scuola definita in alto
            messaggio_parziale = intestazione + f"{ICON_SCUOLA} "
            
            for i, aula in enumerate(lista_aule):
                aula = aula.strip()
                testo_aula = aula + (", " if i < len(lista_aule)-1 else "")
                
                if len(messaggio_parziale) + len(testo_aula) > 4000:
                    await update.message.reply_text(messaggio_parziale, parse_mode='HTML', disable_web_page_preview=True)
                    messaggio_parziale = "<i>(continua)...</i> " + testo_aula
                else:
                    messaggio_parziale += testo_aula
            
            if messaggio_parziale:
                await update.message.reply_text(messaggio_parziale + "\n" + SEPARATORE, parse_mode='HTML', disable_web_page_preview=True)
            continue 

        # CASO NORMALE
        if len(chunk) + len(pezzo_completo) > 4000:
            await update.message.reply_text(chunk, parse_mode='HTML', disable_web_page_preview=True)
            chunk = ""
        
        chunk += pezzo_completo
        
    if chunk:
        await update.message.reply_text(chunk, parse_mode='HTML', disable_web_page_preview=True)


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
    
    print(AVVIO)
    app.run_polling()
