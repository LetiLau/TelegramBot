import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from appunti_bot.content import CATALOGO
from appunti_bot.utils import invia_ordine_generico

# Chiavi per il catalogo
KEY_ANNO = "anno_1"
KEY_MATERIA = "fisica_1"

# Prefisso callback
PREFIX = "f1_"

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    try:
        dati = CATALOGO[KEY_ANNO][KEY_MATERIA]
    except KeyError:
        await query.answer("Errore catalogo!", show_alert=True)
        return

    # --- INVIO DEMO ---
    file_path = dati.get("file_demo", "")
    try: await query.message.delete()
    except: pass 

    if os.path.exists(file_path):
        msg_wait = await context.bot.send_message(query.message.chat_id, "⏳ <i>Invio demo...</i>", parse_mode='HTML')
        try:
            with open(file_path, 'rb') as f:
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=f,
                    caption=f"📄 <b>Anteprima: {dati.get('titolo', 'Appunti')}</b>",
                    parse_mode='HTML'
                )
            try: await msg_wait.delete()
            except: pass
        except: pass
    else:
        await query.answer("⚠️ Demo non disponibile", show_alert=True)

    # --- RECUPERO DATI ---
    titolo = dati.get('titolo', 'Titolo N/D')
    prof = dati.get('prof', 'Prof. N/D')
    anno = dati.get('anno_accademico', 'N/D')
    desc = dati.get('descrizione', '')
    libro = dati.get('libro', 'N/D')
    
    # Prezzi letti dal catalogo
    p_base = dati.get('prezzo', 'N/D')      # Prezzo solo appunti
    p_full = dati.get('prezzo_full', 'N/D') # Prezzo pacchetto
    
    formati = dati.get('formati', [])
    formati_txt = "\n".join([f"- {f}" for f in formati])

    # --- TESTO MESSAGGIO ---
    testo = (
        f"<b>{titolo}</b>\n"
        f"👤 {prof} (a.a. {anno})\n\n"
        f"📚 Libro di riferimento: {libro}\n"
        f"{desc}\n"
        f"💾 <b>Formati disponibili:</b>\n {formati_txt}\n\n"
        "(Pagamento e preferenze gestiti in chat💬)\n\n"
        "👇 <b>Seleziona l'opzione di acquisto:</b>"
    )
    
    # --- BOTTONI DINAMICI ---
    kb = [
        # Tasto 1: Solo Appunti (legge p_base)
        [InlineKeyboardButton(f"1️⃣ Solo Appunti ({p_base})", callback_data=f'{PREFIX}buy_base')],
        
        # Tasto 2: Pacchetto Full (legge p_full)
        [InlineKeyboardButton(f"2️⃣ Pacchetto FULL ({p_full})", callback_data=f'{PREFIX}buy_full')],
        
        [InlineKeyboardButton("🔙 Indietro", callback_data='selAnno_' + KEY_ANNO)]
    ]
    
    await context.bot.send_message(
        chat_id=query.message.chat_id, 
        text=testo, 
        reply_markup=InlineKeyboardMarkup(kb), 
        parse_mode='HTML'
    )


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    # Rileggiamo i dati per avere i prezzi aggiornati
    dati = CATALOGO[KEY_ANNO][KEY_MATERIA]
    
    if data == f'{PREFIX}buy_base':
        await invia_ordine_generico(
            update, context,
            titolo_materia=dati.get('titolo'),
            dettaglio_ordine="Solo Appunti (Versione Base)",
            prezzo_totale=dati.get('prezzo') # Legge 12€
        )
        
    elif data == f'{PREFIX}buy_full':
        await invia_ordine_generico(
            update, context,
            titolo_materia=dati.get('titolo'),
            dettaglio_ordine="🔴 PACCHETTO FULL (+Extra)",
            prezzo_totale=dati.get('prezzo_full') # Legge 16€
        )
