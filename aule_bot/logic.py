import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Import relativi
from . import utils
from . import scraper

TOKEN = os.getenv("ROOMS_BOT")
ADMIN_ID = os.getenv("ADMIN_ID") 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- 🎨 SEZIONE ESTETICA 🎨 ---
SEPARATORE = "───────────────"

HEADER_AULE_ALL = "🎓 **TUTTE LE AULE LIBERE** 🎓\n📍 (Clicca sul nome per la mappa)\n"
HEADER_PRESE    = "🔌 **SOLO CON PRESE** 🔌\n📍 (Clicca sul nome per la mappa)\n"
HEADER_MARATONA = "🏆 **MARATONA STUDIO** 🏆\n(Aule libere per più turni consecutivi)\n"
DISCLAIMER = "\n⚠️ <i>La posizione sulla mappa indica l'ingresso del padiglione.</i>"

ICON_OROLOGIO = "🕒"
ICON_SCUOLA   = "🏫" 
ICON_FUOCO    = "🔥"
ICON_PIN      = "📍"
# -----------------------------

# --- TASTIERA (MENU AZIONI) ---
def get_tastiera_azioni():
    """Restituisce i bottoni per le azioni principali"""
    keyboard = [
        [
            InlineKeyboardButton("🎓 Tutte le Aule", callback_data='aule_all'),
            InlineKeyboardButton("🔌 Solo Prese", callback_data='prese')
        ],
        [
            InlineKeyboardButton("🏃‍♂️ Maratona (3h+)", callback_data='maratona')
        ]
        # Nota: Non mettiamo Info/Help qui per tenerlo pulito e veloce
    ]
    return InlineKeyboardMarkup(keyboard)

# --- FUNZIONI COMUNI ---

async def invia_lungo(update, testo):
    """Gestisce l'invio e attacca i BOTTONI alla fine dell'ultimo messaggio"""
    messaggio_telegram = update.effective_message
    
    blocchi = testo.split(SEPARATORE)
    chunk = ""
    totale_blocchi = len(blocchi)
    
    # Prepariamo i blocchi puliti
    blocchi_puliti = [b for b in blocchi if b.strip()]
    
    for indice, blocco in enumerate(blocchi_puliti):
        pezzo_completo = blocco.strip() + "\n" + SEPARATORE + "\n"
        
        # Logica per capire se è l'ULTIMO pezzo da inviare
        # Se siamo all'ultimo blocco, attaccheremo i bottoni
        is_ultimo_blocco = (indice == len(blocchi_puliti) - 1)
        
        # --- GESTIONE BLOCCO GIGANTE (>4000) ---
        if len(pezzo_completo) > 4000:
            if chunk:
                await messaggio_telegram.reply_text(chunk, parse_mode='HTML', disable_web_page_preview=True)
                chunk = ""
            
            righe = pezzo_completo.split('\n')
            idx_aule = -1
            icona_usata = ""
            
            for i, riga in enumerate(righe):
                if ICON_SCUOLA in riga: 
                    idx_aule = i
                    icona_usata = ICON_SCUOLA + " "
                    break
                elif ICON_PIN in riga: 
                    idx_aule = i
                    icona_usata = ICON_PIN + " "
                    break
            
            if idx_aule != -1:
                intestazione = "\n".join(righe[:idx_aule]) + "\n" + icona_usata
                corpo_aule = righe[idx_aule].replace(icona_usata, "", 1)
            else:
                intestazione = righe[0] + "\n"
                corpo_aule = "\n".join(righe[1:-2])

            lista_aule = corpo_aule.split(',')
            messaggio_parziale = intestazione
            
            for i, aula in enumerate(lista_aule):
                aula = aula.strip()
                testo_aula = aula + (", " if i < len(lista_aule)-1 else "")
                
                if len(messaggio_parziale) + len(testo_aula) > 4000:
                    await messaggio_telegram.reply_text(messaggio_parziale, parse_mode='HTML', disable_web_page_preview=True)
                    messaggio_parziale = "<i>(continua)...</i> " + testo_aula
                else:
                    messaggio_parziale += testo_aula
            
            # Invio ultimo pezzo del blocco gigante
            if messaggio_parziale:
                # Se era l'ultimo blocco in assoluto, metto i bottoni qui
                tastiera = get_tastiera_azioni() if is_ultimo_blocco else None
                await messaggio_telegram.reply_text(messaggio_parziale + "\n" + SEPARATORE, parse_mode='HTML', disable_web_page_preview=True, reply_markup=tastiera)
            continue 

        # --- GESTIONE NORMALE ---
        if len(chunk) + len(pezzo_completo) > 4000:
            await messaggio_telegram.reply_text(chunk, parse_mode='HTML', disable_web_page_preview=True)
            chunk = ""
        
        chunk += pezzo_completo
        
    # Invio rimasuglio finale (qui vanno i bottoni al 99% dei casi)
    if chunk:
        await messaggio_telegram.reply_text(chunk, parse_mode='HTML', disable_web_page_preview=True, reply_markup=get_tastiera_azioni())

# --- COMANDI AZIONE ---

async def aule_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.effective_message.reply_text("🔎 <b>Cerco tutte le aule...</b>", parse_mode='HTML')
    else:
        await update.message.reply_text("🔎 <b>Cerco tutte le aule...</b>", parse_mode='HTML')

    dati = scraper.scarica_dati_swas() 
    
    if not dati:
        await update.effective_message.reply_text("❌ Errore sito Polito.")
        return

    messaggio = [HEADER_AULE_ALL]
    for orario, lista_aule in dati.items():
        nomi_belli = [utils.formatta_nome(a) for a in lista_aule]
        testo = ", ".join(nomi_belli)
        blocco = f"{ICON_OROLOGIO} {orario}\n{ICON_SCUOLA} {testo}\n{SEPARATORE}"
        messaggio.append(blocco)
    
    messaggio.append(DISCLAIMER)
    await invia_lungo(update, "\n".join(messaggio))

async def prese(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.effective_message.reply_text("🔌 <b>Filtro solo prese...</b>", parse_mode='HTML')
    else:
        await update.message.reply_text("🔌 <b>Filtro solo prese...</b>", parse_mode='HTML')

    dati = scraper.scarica_dati_swas()
    if not dati: return

    messaggio = [HEADER_PRESE]
    for orario, lista_aule in dati.items():
        lista_prese = [utils.formatta_nome(a, mostra_icona=False) for a in lista_aule if utils.controlla_presa(a)]
        if lista_prese:
            blocco = f"{ICON_OROLOGIO} {orario}\n{ICON_SCUOLA} {', '.join(lista_prese)}\n{SEPARATORE}"
            messaggio.append(blocco)
            
    messaggio.append(DISCLAIMER)
    await invia_lungo(update, "\n".join(messaggio))

async def maratona(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.effective_message.reply_text("🏃‍♂️ <b>Calcolo Maratona Studio...</b>", parse_mode='HTML')
    else:
        await update.message.reply_text("🏃‍♂️ <b>Calcolo Maratona Studio...</b>", parse_mode='HTML')

    dati = scraper.scarica_dati_swas()
    if not dati or len(dati) < 2:
        await update.effective_message.reply_text("⚠️ Troppe poche fasce orarie oggi.")
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

# --- COMANDI INFORMATIVI ---

async def info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando Info richiesto"""
    if update.callback_query: await update.callback_query.answer()
    
    testo = (
        "ℹ️ <b>INFO BOT</b>\n\n"
        "Questo bot scarica in tempo reale i dati dal sito ufficiale SWAS del PoliTo.\n\n"
        "📌 <b>Sede:</b> Corso Duca degli Abruzzi (Centrale)\n"
        "🔌 <b>Prese:</b> Il database delle prese è aggiornato manualmente dagli studenti.\n\n"
        "<i>Hai trovato un errore o vuoi suggerire una funzione?</i>\n"
        "Usa il comando /suggest seguito dal messaggio!"
    )
    await update.effective_message.reply_text(testo, parse_mode='HTML')

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Il vecchio help descrittivo, ma con i tasti alla fine"""
    if update.callback_query: await update.callback_query.answer()
    
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
    # Aggiungiamo i bottoni anche qui per comodità
    await update.effective_message.reply_text(testo, parse_mode='HTML', reply_markup=get_tastiera_azioni())

async def suggest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messaggio_utente = " ".join(context.args)
    if not messaggio_utente:
        await update.message.reply_text("⚠️ Scrivi il tuo messaggio dopo il comando.\nEs: <code>/suggest Aggiungi aula 5</code>", parse_mode='HTML')
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

# --- START & GESTORE CLICK ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sequenza: Saluto -> Info -> Help (con tasti)"""
    user_name = update.effective_user.first_name
    
    # 1. Saluto
    await update.message.reply_text(f"Ciao {user_name}! 👋\nBenvenuto nel <b>Bot Aule PoliTo</b>.", parse_mode='HTML')
    
    # 2. Info tecnica
    await info_cmd(update, context)
    
    # 3. Guida comandi (che contiene i tasti alla fine)
    await help_cmd(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i click sui bottoni"""
    query = update.callback_query
    data = query.data
    
    if data == 'aule_all':
        await aule_all(update, context)
    elif data == 'prese':
        await prese(update, context)
    elif data == 'maratona':
        await maratona(update, context)

# --- SETUP ---
def setup_bot():
    if not TOKEN:
        print("⚠️ AuleBot: Token mancante!")
        return None

    utils.carica_prese()

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_cmd))
    application.add_handler(CommandHandler('info', info_cmd))
    application.add_handler(CommandHandler('auleAll', aule_all))
    application.add_handler(CommandHandler('auleall', aule_all))
    application.add_handler(CommandHandler('aule', aule_all))
    application.add_handler(CommandHandler('prese', prese))
    application.add_handler(CommandHandler('maratona', maratona))
    application.add_handler(CommandHandler('suggest', suggest))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    
    return application
