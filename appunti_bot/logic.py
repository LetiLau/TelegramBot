import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# 1. Importiamo il Catalogo (i Dati)
from .content import CATALOGO

# 2. Importiamo i moduli specifici (le Logiche di vendita)
from .materie import fisica1             # <--- Nome del FILE .py
from .materie import chimica
from .materie import algebra_geom
from .materie import elettrom_elettrotec

TOKEN = os.getenv("APPUNTI_BOT")

# 3. MAPPA DI COLLEGAMENTO
# Associa la "chiave" del catalogo al "modulo python" che deve gestirla
MODULE_MAP = {
    # "CHIAVE_CATALOGO" : NOME_FILE_IMPORTATO
    "fisica_1": fisica1,
    "chimica": chimica,
    "algebra-geometria": algebra_geom,
    "elettromag_elettrotec": elettrom_elettrotec
}

# --- MENU PRINCIPALE (Scelta Anno) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Genera dinamicamente i pulsanti basandosi sugli ANNI nel Catalogo.
    """
    keyboard = []
    
    # Itera su "anno_1", "anno_2" nel catalogo
    for key_anno in CATALOGO.keys():
        # Rende la scritta carina: "anno_1" -> "📂 Anno 1"
        label = f"📂 {key_anno.replace('_', ' ').title()}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"selAnno_{key_anno}")])
    
    user_name=update.effective_user.first_name
    
    testo = (
        f"👋 Ciao {user_name}! Benvenuto nel **Bot degli Appunti**.\n\n"
        "Seleziona il tuo anno per vedere le materie disponibili⬇️:"
    )
    
    # Logica intelligente:
    # Se è un comando (/start) OPPURE se abbiamo chiesto un messaggio nuovo (force_new)
    # allora usiamo send_message.
    if update.message or force_new:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id=chat_id, text=testo, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        # Altrimenti modifichiamo il messaggio esistente (comportamento classico)
        await update.callback_query.edit_message_text(testo, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        
# --- MENU MATERIE (Scelta Corso) ---
async def menu_materie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Genera i pulsanti delle materie leggendo il Catalogo dell'anno scelto.
    """
    query = update.callback_query
    await query.answer()
    
    # data format: selAnno_anno_1
    anno_scelto = query.data.replace("selAnno_", "")
    
    if anno_scelto not in CATALOGO:
        await query.answer("Anno non trovato!", show_alert=True)
        return

    materie = CATALOGO[anno_scelto]
    keyboard = []
    
    # Itera sulle materie (es. fisica_1, chimica...)
    for key_materia, info in materie.items():
        # Prende il "titolo" dal catalogo (es. "⚛️ Fisica 1")
        titolo = info.get("titolo", key_materia)
        # Callback format: open_anno_1_fisica_1
        keyboard.append([InlineKeyboardButton(titolo, callback_data=f"open_{anno_scelto}_{key_materia}")])
        
    # Tasto Indietro
    keyboard.append([InlineKeyboardButton("🔙 Torna agli Anni", callback_data="main_start")])
    
    await query.edit_message_text(
        f"📂 **Materie disponibili per {anno_scelto.replace('_', ' ')}:**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# --- ROUTER INTELLIGENTE ---
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    # 1. Torna alla Home (Metodo Classico - Sovrascrive)
    if data == 'main_start':
        await start(update, context)
        return

    # 1-BIS. Torna alla Home (NUOVO Metodo - Mantiene lo scontrino)
    elif data == 'return_home_new':
        await query.answer() # Toglie l'orologio di caricamento dal bottone
        await start(update, context, force_new=True) # Chiama start forzando un nuovo messaggio
        return

    # 2. Scelta dell'Anno -> Mostra Materie
    elif data.startswith('selAnno_'):
        await menu_materie(update, context)
        return

    # 3. Apertura Materia Specifica (Dispatche al modulo giusto)
    elif data.startswith('open_'):
        # data format: open_anno_1_fisica_1
        parti = data.split("_")
        # Ricostruiamo la chiave materia unendo i pezzi dal terzo in poi
        # parti[0]=open, parti[1]=anno, parti[2]=1, resto...
        chiave_materia = "_".join(parti[3:]) 
        
        # Cerchiamo il modulo nella MAPPA
        if chiave_materia in MODULE_MAP:
            modulo = MODULE_MAP[chiave_materia]
            # Passiamo il controllo alla funzione 'menu' del file specifico
            await modulo.menu(update, context)
        else:
            await query.answer(f"⚠️ Modulo per '{chiave_materia}' non ancora pronto!", show_alert=True)
        return

    # 4. Gestione Callback Specifiche dei Moduli
    # Qui intercettiamo i click interni ai file (es. f1_buy, alg_buy...)
    # Ogni modulo deve avere un suo prefisso unico riconoscibile
    
    elif data.startswith('f1_'):      # Prefisso Fisica 1
        await fisica1.handler(update, context)
        
    elif data.startswith('ch_'):      # Prefisso Chimica
        await chimica.handler(update, context)
        
    elif data.startswith('alg_'):     # Prefisso Algebra
        await algebra_geom.handler(update, context)
        
    elif data.startswith('em_'):      # Prefisso Elettrotecnica
        await elettrom_elettrotec.handler(update, context)

# --- SETUP ---
def setup_bot():
    if not TOKEN: return None
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(router))
    return app
