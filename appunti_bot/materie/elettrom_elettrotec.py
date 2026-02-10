import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from appunti_bot.content import CATALOGO
from appunti_bot.utils import invia_ordine_generico

# Chiavi catalogo
KEY_ANNO = "anno_2"
KEY_MATERIA = "elettrom_elettrotec"

# Prefisso callback
PREFIX = "em_" 

# --- 1. MENU PRINCIPALE (LANDING PAGE) ---
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    try: dati = CATALOGO[KEY_ANNO][KEY_MATERIA]
    except: await query.answer("Errore dati", show_alert=True); return

    # --- INVIO DEMO UNICA ---
    file_path = dati.get("file_demo", "")
    try: await query.message.delete()
    except: pass 

    if os.path.exists(file_path):
        msg_wait = await context.bot.send_message(query.message.chat_id, "⏳ <i>Invio demo completa...</i>", parse_mode='HTML')
        try:
            with open(file_path, 'rb') as f:
                await context.bot.send_document(chat_id=query.message.chat_id, document=f, caption=f"📄 <b>Anteprima: {dati.get('titolo')}</b>", parse_mode='HTML')
            try: await msg_wait.delete()
            except: pass
        except: pass
    
    # Dati per la copertina
    prof_el = dati["mod_elettro"].get("prof", "N/D")
    prof_f2 = dati["mod_fisica2"].get("prof", "N/D")
    p_full = dati.get("prezzo_completo", "N/D")

    testo = (
        f"⚡ <b>{dati.get('titolo')}</b>\n\n"
        "Corso diviso in due moduli. Puoi acquistarli singolarmente o insieme.\n\n"
        f"👤 <b>Elettrotecnica:</b> {prof_el}\n"
        f"👤 <b>Fisica 2:</b> {prof_f2}\n\n"
        "👇 <b>Cosa vuoi visualizzare?</b>"
    )
    
    kb = [
        [InlineKeyboardButton(f"📦 INFO PACCHETTO COMPLETO ({p_full})", callback_data=f'{PREFIX}show_full')],
        [InlineKeyboardButton("⚡ Solo Elettrotecnica", callback_data=f'{PREFIX}show_elettro')],
        [InlineKeyboardButton("🧲 Solo Fisica 2", callback_data=f'{PREFIX}show_fis2')],
        [InlineKeyboardButton("🔙 Torna all'Anno", callback_data=f'selAnno_{KEY_ANNO}')]
    ]
    
    await context.bot.send_message(chat_id=query.message.chat_id, text=testo, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')


# --- 2. SCHEDA: PACCHETTO COMPLETO ---
async def show_full_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dati = CATALOGO[KEY_ANNO][KEY_MATERIA]
    
    # Uniamo i nomi dei prof
    prof_el = dati["mod_elettro"].get("prof", "")
    prof_f2 = dati["mod_fisica2"].get("prof", "")
    
    formati = dati.get('formati_full', [])
    formati_txt = "\n".join([f"- {f}" for f in formati])

    global anno
    anno = dati.get('anno_accademico', 'N/D')
    
    testo = (
        f"📦 <b>PACCHETTO COMPLETO</b>\n"
        f"Include Elettrotecnica & Fisica 2.\n\n"
        f"👤 <b>Prof:</b> {prof_el} & {prof_f2}\n\n"
        f"{dati.get('descrizione_full')}\n\n"
        f"💾 <b>Formati inclusi:</b> {formati}\n"
        f"💰 Prezzo Totale: <b>{dati.get('prezzo_completo')}</b>"
    )
    
    kb = [
        [InlineKeyboardButton("✅ COMPRA PACCHETTO COMPLETO", callback_data=f'{PREFIX}buy_everything')],
        [InlineKeyboardButton("🔙 Indietro", callback_data=f'{PREFIX}menu_main')]
    ]
    
    await query.edit_message_text(text=testo, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')


# --- 3. SCHEDA: SOLO ELETTROTECNICA ---
async def show_elettro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dati = CATALOGO[KEY_ANNO][KEY_MATERIA]["mod_elettro"]
    
    formati = dati.get('formati', [])
    formati_txt = "\n".join([f"- {f}" for f in formati])
    
    testo = (
        f"<b>{dati['nome']}</b>\n"
        f"👤 {dati['prof']} (a.a. {anno})\n\n"
        f"{dati['descrizione']}\n\n"
        f"💾 <b>Formati disponibili:</b> {formati}\n"
        f"💰 Prezzo: <b>{dati['prezzo']}</b>"
    )
    
    kb = [
        [InlineKeyboardButton("✅ Compra Elettrotecnica", callback_data=f'{PREFIX}buy_elettro')],
        [InlineKeyboardButton("🔙 Indietro", callback_data=f'{PREFIX}menu_main')]
    ]
    
    await query.edit_message_text(text=testo, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')


# --- 4. SCHEDA: SOLO FISICA 2 ---
async def show_fisica2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dati = CATALOGO[KEY_ANNO][KEY_MATERIA]["mod_fisica2"]
    
    formati = dati.get('formati', [])
    formati_txt = "\n".join([f"- {f}" for f in formati])
    
    
    p_base = dati.get("prezzo_base")
    p_full = dati.get("prezzo_full")
    
    testo = (
        f"<b>{dati['nome']}</b>\n"
        f"👤 {dati['prof']} (a.a. {anno})\n\n"
        f"{dati['descrizione']}\n\n"
        f"💾 <b>Formati disponibili:</b> {formati}\n\n"
        "👇 <b>Scegli la versione che vuoi acquistare:</b>"
    )
    
    kb = [
        [InlineKeyboardButton(f"1️⃣ Solo Appunti ({p_base})", callback_data=f'{PREFIX}buy_fis2_base')],
        [InlineKeyboardButton(f"2️⃣ Appunti + Esercizi ({p_full})", callback_data=f'{PREFIX}buy_fis2_full')],
        [InlineKeyboardButton("🔙 Indietro", callback_data=f'{PREFIX}menu_main')]
    ]
    
    await query.edit_message_text(text=testo, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')


# --- 5. HANDLER E ACQUISTI ---
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    dati_main = CATALOGO[KEY_ANNO][KEY_MATERIA]
    
    # Navigazione
    if data == f'{PREFIX}menu_main':
        await menu(update, context) 
        
    elif data == f'{PREFIX}show_full':
        await show_full_package(update, context)
        
    elif data == f'{PREFIX}show_elettro':
        await show_elettro(update, context)
        
    elif data == f'{PREFIX}show_fis2':
        await show_fisica2(update, context)
        
    # --- ACQUISTI ---
    
    elif data == f'{PREFIX}buy_everything':
        await invia_ordine_generico(
            update, context,
            titolo_materia=dati_main['titolo'],
            dettaglio_ordine="📦 PACCHETTO COMPLETO (Elettrotecnica + Fisica 2)",
            prezzo_totale=dati_main['prezzo_completo']
        )

    elif data == f'{PREFIX}buy_elettro':
        sub = dati_main["mod_elettro"]
        await invia_ordine_generico(
            update, context,
            titolo_materia=sub['nome'],
            dettaglio_ordine="⚡ Solo Elettrotecnica",
            prezzo_totale=sub['prezzo']
        )

    elif data == f'{PREFIX}buy_fis2_base':
        sub = dati_main["mod_fisica2"]
        await invia_ordine_generico(
            update, context,
            titolo_materia=sub['nome'],
            dettaglio_ordine="🧲 Solo Appunti Fisica 2 (Versione Base)",
            prezzo_totale=sub['prezzo_base']
        )

    elif data == f'{PREFIX}buy_fis2_full':
        sub = dati_main["mod_fisica2"]
        await invia_ordine_generico(
            update, context,
            titolo_materia=sub['nome'],
            dettaglio_ordine="🧲✏️ Fisica 2 COMPLETA (+Esercizi)",
            prezzo_totale=sub['prezzo_full']
        )
