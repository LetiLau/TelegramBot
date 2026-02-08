import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from .content import CATALOGO

# --- CONFIGURAZIONE ---
# ID del venditore (TU) per ricevere le notifiche
ADMIN_ID = os.getenv("ADMIN_ID")

TOKEN = os.getenv("APPUNTI_BOT")

# DATABASE DEI CORSI (Facile da espandere)
# Struttura: Anno -> Codice_Materia -> Dettagli
# CATALOGO = {
#     "anno_1": {
#         "fisica_1": {
#             "nome": "⚛️ Fisica 1",
#             "descrizione": "Teoria completa + Esercizi svolti. Ottimo per lo scritto.",
#             "prezzo": "12,00€",
#             "file_demo": "appunti_bot/files/demo-fisica1.pdf"
#         },
#         "chimica": {
#             "nome": "🧪 Chimica",
#             "descrizione": "Limiti, derivate, integrali e serie.",
#             "prezzo": "10,00€",
#             "file_demo": "appunti_bot/files/demo-chimica.pdf" # Esempio futuro
#         }
#     },
#     "anno_2": {
#         # Puoi aggiungere materie qui in futuro
#     }
# }

# --- 1. MENU PRINCIPALE (Scelta Anno) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra la scelta dell'anno."""
    keyboard = [
        [InlineKeyboardButton("1️⃣ Primo Anno", callback_data='menu_anno_1')],
        [InlineKeyboardButton("2️⃣ Secondo Anno (Presto...)", callback_data='menu_anno_2')],
    ]

    user_name=update.effective_user.first_name
    
    testo = (
        f"👋 Ciao {user_name}! Benvennuto nel **Bot degli Appunti**.\n\n"
        "Seleziona il tuo anno per vedere le materie disponibili⬇️:"
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
# FILE: appunti_bot/logic.py
# (Ricordati gli import soliti in cima)

async def info_materia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 1. Parsing dati
    parti = query.data.split("_") 
    chiave_anno = f"{parti[1]}_{parti[2]}"
    chiave_materia = "_".join(parti[3:])

    try:
        dati = CATALOGO[chiave_anno][chiave_materia]
    except KeyError:
        await query.answer("Errore: Materia non trovata!", show_alert=True)
        return

    # Cancelliamo il vecchio messaggio
    try:
        await query.message.delete()
    except:
        pass 

    file_path = dati.get("file_demo", "") # Usa .get per sicurezza
    file_esiste = os.path.exists(file_path)
    
    # --- GESTIONE PDF ---
    testo_intro = ""
    
    if file_esiste:
        await query.answer("Invio demo in corso...") 
        try:
            with open(file_path, 'rb') as f:
                # Titolo della demo sicuro
                titolo_safe = dati.get('titolo', 'Appunti')
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=f,
                    caption=f"📄 <b>Anteprima: {titolo_safe}</b>",
                    parse_mode='HTML'
                )
            testo_intro = "☝️ <b>Qui sopra trovi la demo.</b>"
        except Exception as e:
            testo_intro = "⚠️ <b>Errore invio PDF.</b>"
    else:
        await query.answer("⚠️ Demo PDF non ancora caricata.", show_alert=True)
        testo_intro = "⚠️ <b>Anteprima PDF non ancora disponibile.</b>"

    # --- RECUPERO DATI SICURO (Anti-Crash) ---
    # Se il dato manca nel content.py, usiamo il valore di default (secondo argomento)
    
    titolo = dati.get('titolo', 'Titolo Sconosciuto')
    prof = dati.get('prof', 'Prof. N/D')
    anno = dati.get('anno_accademico', 'N/D')
    
    # Recuperiamo il libro (se manca mette 'Non specificato')
    libro = dati.get('libro', 'Non specificato') 
    
    descrizione = dati.get('descrizione', 'Descrizione non disponibile.')
    prezzo = dati.get('prezzo', 'N/D')
    
    # Formattazione lista formati
    lista_formati = dati.get('formati', ['PDF'])
    formati_stringa = "\n".join([f"- {f}" for f in lista_formati])

    # --- IMPAGINAZIONE MESSAGGIO (Aggiornata) ---
    testo_finale = (
        f"{testo_intro}\n\n"
        f"📚 <b>{titolo}</b>\n"
        f"👤 {prof} (a.a. {anno})\n"
        f"📖 <b>Libro rif.:</b> {libro}\n\n"  # <--- RIGA AGGIUNTA QUI
        f"{descrizione}\n\n"
        f"💾 <b>Formati:</b>\n{formati_stringa}\n\n"
        f"💰 Prezzo: <b>{prezzo}</b>\n\n"
        "Cosa vuoi fare ora?"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ LO VOGLIO COMPRARE", callback_data=f'buy_{chiave_anno}_{chiave_materia}')],
        [InlineKeyboardButton("🔙 Scegli altra materia", callback_data=f'menu_{chiave_anno}')]
    ]

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=testo_finale,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


# --- 4. GESTIONE ORDINE (Notifica all'Admin) ---
# FILE: appunti_bot/logic.py

async def richiesta_acquisto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    
    parti = query.data.split("_")
    chiave_anno = f"{parti[1]}_{parti[2]}"
    chiave_materia = "_".join(parti[3:])
    
    try:
        dati = CATALOGO[chiave_anno][chiave_materia]
    except KeyError:
        await query.edit_message_text("Errore: Articolo non più disponibile.")
        return
    
    # --- RECUPERO DATI SICURO (.get) ---
    # Usiamo .get() anche qui. Se manca il titolo, usa "Appunti Generici"
    nome_materia = dati.get('titolo', 'Appunti Generici') 
    prezzo = dati.get('prezzo', 'N/D')
    
    # Prepariamo il messaggio per l'ADMIN
    user_link = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    username_txt = f"@{user.username}" if user.username else "Nessun Username"
    
    msg_admin = (
        "💰 <b>NUOVO CLIENTE!</b>\n\n"
        f"👤 <b>Utente:</b> {user_link} ({username_txt})\n"
        f"📚 <b>Vuole:</b> {nome_materia}\n"  # Qui ora è sicuro
        f"💶 <b>Prezzo:</b> {prezzo}\n"       # Qui ora è sicuro
    )

    # ... (il resto del codice invio admin e risposta utente rimane uguale) ...



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
