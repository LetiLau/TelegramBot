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
            "file_demo": "appunti_bot/files/demo_fisica1.pdf" 
        },
        "chimica": {
            "nome": "🧪 Chimica",
            "descrizione": "Limiti, derivate, integrali e serie.",
            "prezzo": "10,00€",
            "file_demo": "appunti_bot/files/demo_analisi1.pdf" # Esempio futuro
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
    
    testo = (
        "👋 **Ciao! Sono il Bot degli Appunti.**\n\n"
        "Seleziona il tuo anno per vedere le materie disponibili:"
    )
    
    # Se è un nuovo messaggio o una modifica di uno esistente
    if update.message:
        await update.message.reply_text(testo, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(testo, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

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
async def info_materia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Invio demo in corso...") # Feedback immediato
    
    # Parsing dei dati: info_anno_1_fisica_1
    _, anno, materia = query.data.split("_", 2)
    dati = CATALOGO[anno][materia]
    
    # Testo della scheda
    testo = (
        f"📚 **{dati['nome']}**\n\n"
        f"📝 {dati['descrizione']}\n"
        f"💰 Prezzo: **{dati['prezzo']}**\n\n"
        "👇 *Qui sotto trovi l'anteprima PDF gratuita.*"
    )
    
    # Pulsante per ORDINARE
    keyboard = [
        [InlineKeyboardButton("✅ LO VOGLIO COMPRARE", callback_data=f'buy_{anno}_{materia}')],
        [InlineKeyboardButton("🔙 Torna alle materie", callback_data=f'menu_{anno}')]
    ]

    # 1. Modifica il messaggio testo con le info e i bottoni
    await query.edit_message_text(testo, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    
    # 2. Invia il file PDF Demo (se esiste)
    file_path = dati["file_demo"]
    chat_id = query.message.chat_id
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=chat_id,
                document=f,
                caption=f"Anteprima di {dati['nome']} 📄"
            )
    else:
        # Se ti sei dimenticato di caricare il file su GitHub/Render
        await context.bot.send_message(chat_id, "⚠️ Demo non trovata (l'admin la sta caricando!).")

# --- 4. GESTIONE ORDINE (Notifica all'Admin) ---
async def richiesta_acquisto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    _, anno, materia = query.data.split("_", 2)
    dati = CATALOGO[anno][materia]
    
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

    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(router)) # Unico handler che smista tutto
    
    return app
