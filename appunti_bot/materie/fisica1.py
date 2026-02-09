import os  # <--- MANCAVA QUESTO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from appunti_bot.content import CATALOGO
from appunti_bot.utils import invia_ordine_generico

# Prefisso callback: f1_

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dati = CATALOGO["anno_1"]["fisica_1"]
    
    # --- MANCAVA QUESTA RIGA ---
    file_path = dati.get("file_demo", "") 
    # ---------------------------

    # 1. Pulizia: Cancelliamo il vecchio messaggio
    try:
        await query.message.delete()
    except:
        pass 

    # 2. Gestione Invio File
    if os.path.exists(file_path):
        msg_wait = await context.bot.send_message(query.message.chat_id, "⏳ <i>Invio demo in corso...</i>", parse_mode='HTML')
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
        except Exception as e:
            await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=msg_wait.message_id, text="⚠️ Errore tecnico nell'invio del file.")
    else:
        # Se vuoi nascondere l'avviso se il file non c'è, commenta questa riga:
        await query.answer("⚠️ Demo PDF non ancora disponibile.", show_alert=True)

    # --- TESTO E BOTTONI ---
    testo = (
        f"📚 <b>{dati['titolo']}</b>\n\n"
        "Scegli cosa acquistare:\n"
        "1️⃣ <b>Solo Appunti (12€)</b>: Teoria + Esercizi lezione\n"
        "2️⃣ <b>FULL Pack (16€)</b>: Appunti + Eserciziario Extra + Formulario"
    )
    
    kb = [
        [InlineKeyboardButton("1️⃣ Solo Appunti (12€)", callback_data='f1_buy_base')],
        [InlineKeyboardButton("2️⃣ FULL Pack (16€)", callback_data='f1_buy_full')],
        [InlineKeyboardButton("🔙 Indietro", callback_data='main_start')]
    ]
    
    # Invio messaggio menu
    await context.bot.send_message(query.message.chat_id, testo, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'f1_buy_base':
        await invia_ordine_generico(
            update, context,
            titolo_materia="Fisica 1",
            dettaglio_ordine="Solo Appunti",
            prezzo_totale="12,00€"
        )
        
    elif data == 'f1_buy_full':
        await invia_ordine_generico(
            update, context,
            titolo_materia="Fisica 1",
            dettaglio_ordine="🔴 PACCHETTO FULL (+Extra)",
            prezzo_totale="16,00€"
        )
