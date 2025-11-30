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
        # --- MODIFICA QUI SOTTO: mostra_icona=False ---
        lista_prese = [utils.formatta_nome(a, mostra_icona=False) for a in lista_aule if utils.controlla_presa(a)]
        # ----------------------------------------------
        
        if lista_prese:
            messaggio.append(f"🕒 {orario}\n🏫 {', '.join(lista_prese)}\n───────────────")
            
    messaggio.append("\n⚠️ <i>La posizione sulla mappa indica l'ingresso del padiglione.</i>")
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

    # --- DEBUGGING ---
    print(f"DEBUG: Admin ID letto da variabili: {ADMIN_ID}")
    # -----------------
    
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
        "Mostra le aule che hanno liberi due turni consecutivi (tot. 3h)\n\n"      
        "<i>Presto arriveranno nuove funzioni... stay tuned!</i> 🚀"
    )
    await update.message.reply_text(testo, parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Ciao {user_name}! Ecco tutti i comandi disponibili ⬇️")


# --- GESTIONE MESSAGGI LUNGHI (VERSIONE DEFINITIVA) ---
async def invia_lungo(update, testo):
    SEPARATORE = "───────────────"
    
    # 1. Dividiamo tutto in blocchi orari (ogni blocco è un orario completo)
    blocchi = testo.split(SEPARATORE)
    chunk = "" # Qui accumuliamo il testo da inviare
    
    for blocco in blocchi:
        if not blocco.strip(): continue
        
        # Ricostruiamo il blocco con il separatore estetico
        pezzo_completo = blocco.strip() + "\n" + SEPARATORE + "\n"
        
        # --- CASO A: Il blocco è ENORME (Domenica) ---
        # Da solo supera il limite massimo. Dobbiamo spezzarlo internamente.
        if len(pezzo_completo) > 4000:
            # Prima svuotiamo il buffer se c'era roba vecchia
            if chunk:
                await update.message.reply_text(chunk, parse_mode='HTML', disable_web_page_preview=True)
                chunk = ""
            
            # Ora operiamo sul mostro. Lo dividiamo per righe prima
            righe = pezzo_completo.split('\n')
            intestazione = righe[0] + "\n" # Es: "🕒 08:00 - 23:00"
            
            # Ricostruiamo il corpo delle aule (tutto tranne la prima e l'ultima riga)
            corpo_aule = "\n".join(righe[1:-2]) 
            
            # Dividiamo le aule usando la virgola come bisturi sicuro
            # (Così non tagliamo mai a metà un link HTML <a href...>)
            lista_aule = corpo_aule.split(',')
            
            messaggio_parziale = intestazione + "🏫 "
            
            for i, aula in enumerate(lista_aule):
                aula = aula.strip()
                # Se l'aula ha un link, è lunga. Aggiungiamo virgola se non è l'ultima
                testo_aula = aula + (", " if i < len(lista_aule)-1 else "")
                
                # Se aggiungendo questa aula sforo il limite...
                if len(messaggio_parziale) + len(testo_aula) > 4000:
                    # INVIO IL PEZZO
                    await update.message.reply_text(messaggio_parziale, parse_mode='HTML', disable_web_page_preview=True)
                    # E inizio il pezzo nuovo (senza rimettere l'orario, o mettendolo se vuoi)
                    messaggio_parziale = "<i>(continua fascia precedente)...</i> " + testo_aula
                else:
                    messaggio_parziale += testo_aula
            
            # Inviamo l'ultimo pezzo del mostro con il separatore finale
            if messaggio_parziale:
                await update.message.reply_text(messaggio_parziale + "\n" + SEPARATORE, parse_mode='HTML', disable_web_page_preview=True)
                
            continue # Passiamo al prossimo blocco orario

        # --- CASO B: Il blocco è NORMALE ---
        # Se sommato a quello che ho già supera il limite, invio il vecchio e inizio il nuovo
        if len(chunk) + len(pezzo_completo) > 4000:
            await update.message.reply_text(chunk, parse_mode='HTML', disable_web_page_preview=True)
            chunk = ""
        
        # Aggiungo al buffer
        chunk += pezzo_completo
        
    # Alla fine, se è rimasto qualcosa nel buffer, invialo
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
    
    print("🤖 Bot Avviato!")
    app.run_polling()
