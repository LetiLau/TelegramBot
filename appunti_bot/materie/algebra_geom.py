import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes  # <--- ContextTypes va importato da QUI

# 1. Importiamo i dati e gli strumenti comuni
from ..content import CATALOGO
from ..utils import invia_ordine_generico

# Definiamo dove si trovano i dati nel catalogo
# Così se sposti la materia in "anno_2", cambi solo qui.
KEY_ANNO = "anno_1"
KEY_MATERIA = "algebra-geometria"

# Prefisso per le callback di questo file (deve combaciare con logic.py)
PREFIX = "alg_" 

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mostra la scheda del prodotto leggendo i dati dal Catalogo.
    """
    query = update.callback_query
    
    # Recuperiamo i dati in modo sicuro
    try:
        dati = CATALOGO[KEY_ANNO][KEY_MATERIA]
    except KeyError:
        await query.answer("Errore: Dati materia non trovati!", show_alert=True)
        return

    # --- 1. GESTIONE INVIO DEMO (Standard) ---
    file_path = dati.get("file_demo", "")
    
    # Cancelliamo il menu precedente per pulizia
    try: await query.message.delete()
    except: pass 

    if os.path.exists(file_path):
        # Feedback "Sto inviando..."
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
        except: pass # Se fallisce l'invio (es. file corrotto), andiamo avanti lo stesso
    else:
        # Se non c'è il file, avvisiamo con un popup discreto
        await query.answer("⚠️ Demo PDF non ancora disponibile.", show_alert=True)

    # --- 2. COSTRUZIONE DEL MESSAGGIO ---
    # Usiamo .get() per evitare crash se manca qualche campo
    titolo = dati.get('titolo', 'Titolo N/D')
    prof = dati.get('prof', 'Prof. N/D')
    anno = dati.get('anno_accademico', '')
    desc = dati.get('descrizione', 'Descrizione non disponibile.')
    prezzo = dati.get('prezzo', 'N/D')
    
    # Formattazione lista formati
    formati = dati.get('formati', [])
    formati_txt = "\n".join([f"- {f}" for f in formati])

    testo = (
        f"📚 <b>{titolo}</b>\n"
        f"👤 {prof} ({anno})\n\n"
        f"{desc}\n\n"
        f"💾 <b>Formati inclusi:</b>\n{formati_txt}\n\n"
        f"💰 Prezzo: <b>{prezzo}</b>\n\n"
        "Cosa vuoi fare?"
    )
    
    # --- 3. PULSANTI ---
    # Nota: alg_buy è il segnale per comprare
    kb = [
        [InlineKeyboardButton("✅ LO VOGLIO COMPRARE", callback_data=f'{PREFIX}buy')],
        [InlineKeyboardButton("🔙 Indietro", callback_data='selAnno_' + KEY_ANNO)]
    ]
    
    await context.bot.send_message(
        chat_id=query.message.chat_id, 
        text=testo, 
        reply_markup=InlineKeyboardMarkup(kb), 
        parse_mode='HTML'
    )

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Gestisce i click sui pulsanti di questo modulo (quelli che iniziano con alg_)
    """
    query = update.callback_query
    data = query.data
    
    # Rileggiamo i dati per avere il prezzo aggiornato
    dati = CATALOGO[KEY_ANNO][KEY_MATERIA]
    
    if data == f'{PREFIX}buy':
        # Chiamiamo la funzione generica in utils.py
        await invia_ordine_generico(
            update, context,
            titolo_materia=dati.get('titolo', 'Algebra'),
            dettaglio_ordine="Pacchetto Completo (Unica opzione)",
            prezzo_totale=dati.get('prezzo', 'N/D')
        )
