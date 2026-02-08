import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# --- CONFIGURAZIONE ---
# ID del venditore (TU) per ricevere le notifiche
ADMIN_ID = os.getenv("ADMIN_ID")

TOKEN = os.getenv("APPUNTI_BOT")

# DATABASE DEI CORSI (Facile da espandere)
# Struttura: Anno -> Codice_Materia -> Dettagli
CATALOGO = {
    "anno_1": {
        "fisica_1": {
            "nome": "⚛️ Fisica 1",
            "descrizione": "Teoria completa + Esercizi svolti. Ottimo per lo scritto.",
            "prezzo": "12,00€",
            "file_demo": "appunti_bot/files/demo-fisica1.pdf"
        },
        "chimica": {
            "nome": "🧪 Chimica",
            "descrizione": "Limiti, derivate, integrali e serie.",
            "prezzo": "10,00€",
            "file_demo": "appunti_bot/files/demo-chimica.pdf" # Esempio futuro
        }
    },
    "anno_2": {
        # Puoi aggiungere materie qui in futuro
    }
}

# --- 1. MENU PRINCIPALE (Scelta Anno) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra la scelta dell'anno."""
    keyboard = [
        [InlineKeyboardButton("1️⃣ Primo Anno", callback_data='menu_anno_1')],
        [InlineKeyboardButton("2️⃣ Secondo Anno (Presto...)", callback_data='menu_anno_2')],
    ]

    user_name=update.effective_user.first_name
    
    testo = (
        f"👋 Ciao {user_name}! Benvennuto nel <b>Bot degli Appunti<b>.\n\n"
        "Seleziona il tuo anno per vedere le materie disponibili⬇️:"
    )
    
    # Se è un nuovo messaggio o una modifica di uno esistente
    if update.message:
        await update.message.reply_text(testo, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        await update.callback_query.edit_message_text(testo, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

# --- 2. MENU MATERIE (Dopo aver scelto l'anno) ---
async def menu_materie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    anno = query.data.replace("menu_", "") # es: "anno_1"
    
    if anno not in CATALOGO or not CATALOGO[anno]:
        await query.answer("Nessuna materia disponibile per ora!", show_alert=True)
        return

    # Genera pulsanti dinamicamente dal CATALOGO
    keyboard = []
    for codice_materia, info in CATALOGO[anno].items():
        keyboard.append([InlineKeyboardButton(info["nome"], callback_data=f'info_{anno}_{codice_materia}')])
    
    keyboard.append([InlineKeyboardButton("🔙 Indietro", callback_data='main_start')])
    
    await query.edit_message_text(
        f"📂 **Materie disponibili per {anno.replace('_', ' ')}:**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# --- 3. SCHEDA MATERIA E INVIO DEMO ---
# --- 3. SCHEDA MATERIA E INVIO DEMO (CORRETTA) ---
async def info_materia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # Parsing robusto della stringa: info_anno_1_fisica_1
    # Dividiamo tutto per "_"
    parti = query.data.split("_") 
    # parti sarà: ['info', 'anno', '1', 'fisica', '1']
    
    # Ricostruiamo le chiavi per il dizionario
    chiave_anno = f"{parti[1]}_{parti[2]}"  # diventa "anno_1"
    
    # Per la materia, uniamo tutto ciò che c'è dopo l'anno
    # (così se un domani hai "fisica_tecnica" funziona lo stesso)
    chiave_materia = "_".join(parti[3:])    # diventa "fisica_1"
    
    # Debug (opzionale, se vuoi vedere cosa succede nei log)
    print(f"Certo anno: {chiave_anno}, materia: {chiave_materia}")

    try:
        dati = CATALOGO[chiave_anno][chiave_materia]
    except KeyError:
        await query.answer("Errore: Materia non trovata nel catalogo!", show_alert=True)
        return

    await query.answer("Carico le info...")

    # 1. Testo della scheda (Descrizione + Prezzo)
    testo = (
        f"📚 **{dati['nome']}**\n\n"
        f"📝 {dati['descrizione']}\n\n"
        f"💰 Prezzo: **{dati['prezzo']}**\n"
        "👇 *Sto inviando il PDF Anteprima qui sotto...*"
    )
    
    # Pulsante per ORDINARE
    keyboard = [
        # Passiamo gli stessi dati al bottone compra
        [InlineKeyboardButton("✅ LO VOGLIO COMPRARE", callback_data=f'buy_{chiave_anno}_{chiave_materia}')],
        [InlineKeyboardButton("🔙 Torna alle materie", callback_data=f'menu_{chiave_anno}')]
    ]

    # Invia PRIMA il messaggio di testo (modificando quello precedente)
    await query.edit_message_text(testo, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    # 2. Invia DOPO il file PDF Demo
    file_path = dati["file_demo"]
    chat_id = query.message.chat_id
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=f,
                    caption=f"📄 Anteprima gratuita: {dati['nome']}"
                )
        except Exception as e:
            # Se c'è un errore nell'invio del file (es. file troppo grande o corrotto)
            print(f"Errore invio file: {e}")
            await context.bot.send_message(chat_id, "⚠️ Errore nell'invio del PDF demo.")
    else:
        # Se il file non esiste sul server
        await context.bot.send_message(chat_id, "⚠️ Demo PDF non ancora caricata (contatta l'admin).")

# --- 4. GESTIONE ORDINE (Notifica all'Admin) ---
async def richiesta_acquisto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Parsing robusto (stesso metodo di prima)
    parti = query.data.split("_")
    chiave_anno = f"{parti[1]}_{parti[2]}"  # "anno_1"
    chiave_materia = "_".join(parti[3:])    # "fisica_1"
    
    dati = CATALOGO[chiave_anno][chiave_materia]
    
    # 1. Risposta all'utente (COMPRATORE)
    msg_utente = (
        "✅ **Richiesta inviata!**\n\n"
        f"Ho avvisato il venditore che sei interessato a **{dati['nome']}**.\n"
        "Ti contatterà a breve qui su Telegram per darti il file completo."
    )
    # Rimuoviamo il bottone "Lo voglio" per evitare doppi click
    await query.edit_message_text(msg_utente, parse_mode='Markdown')
    
    # 2. Notifica all'Admin (VENDITORE - TU)
    if ADMIN_ID:
        # Creiamo un link per chattare subito con l'utente
        user_link = f"tg://user?id={user.id}"
        username_txt = f"@{user.username}" if user.username else "Nessun Username"
        
        msg_admin = (
            "💰 **NUOVO CLIENTE!**\n\n"
            f"👤 **Utente:** {user.first_name} ({username_txt})\n"
            f"📚 **Vuole:** {dati['nome']}\n"
            f"💶 **Prezzo:** {dati['prezzo']}\n\n"
            f"👉 [CLICCA QUI PER CONTATTARLO]({user_link})"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg_admin, parse_mode='Markdown')
        except Exception as e:
            print(f"Errore invio notifica admin: {e}")
    else:
        print("⚠️ ADMIN_ID non configurato nelle variabili d'ambiente!")

# --- ROUTER CENTRALE ---
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Smista i click dei bottoni alla funzione giusta."""
    query = update.callback_query
    data = query.data
    
    if data == 'main_start':
        await start(update, context)
    elif data.startswith('menu_'):
        await menu_materie(update, context)
    elif data.startswith('info_'):
        await info_materia(update, context)
    elif data.startswith('buy_'):
        await richiesta_acquisto(update, context)

# --- SETUP ---
def setup_bot():
    if not TOKEN:
        print("⚠️ AppuntiBot: Token mancante!")
        return None

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(router)) # Unico handler che smista tutto
    
    return app
