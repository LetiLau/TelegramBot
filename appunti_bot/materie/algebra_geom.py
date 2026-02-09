from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ContextTypes
from ..utils import invia_ordine_generico
from ..content import CATALOGO # Importiamo i dati se servono (demo, descrizioni)

# Prefisso callback: alg_

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # Recuperiamo i dati dal catalogo
    dati = CATALOGO["anno_1"]["algebra-geometria"]
    
    # Logica invio DEMO (semplificata)
    file_demo = dati.get("file_demo")
  
    # 1. Pulizia: Cancelliamo il vecchio messaggio del menu precedente
    try:
        await query.message.delete()
    except:
        pass 

    # 2. Gestione Invio File
    if os.path.exists(file_path):
        # Feedback visivo immediato
        msg_wait = await context.bot.send_message(query.message.chat_id, "⏳ <i>Invio demo in corso...</i>", parse_mode='HTML')
        
        try:
            with open(file_path, 'rb') as f:
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=f,
                    caption=f"📄 <b>Anteprima: {dati.get('titolo', 'Appunti')}</b>",
                    parse_mode='HTML'
                )
            # Se l'invio riesce, cancelliamo il messaggio "⏳ Invio in corso..."
            try: await msg_wait.delete()
            except: pass
            
        except Exception as e:
            # Se qualcosa va storto nell'invio (es. file troppo grande)
            await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=msg_wait.message_id, text="⚠️ Errore tecnico nell'invio del file.")
    else:
        # Se il file non esiste fisicamente sul server
        # (Opzionale: puoi mandare un avviso o semplicemente non fare nulla e mostrare solo il testo sotto)
        await query.answer("⚠️ Demo PDF non ancora disponibile.", show_alert=True)

    # --- FINE BLOCCO INVIO DEMO ---

  
    testo = (
        f"📚 <b>{dati['titolo']}</b>\n"
        f"👤 {dati['prof']}\n\n"
        f"{dati['descrizione']}\n\n"
        f"💰 Prezzo: <b>{dati['prezzo']}</b>"
    )
    
    kb = [
        # Callback specifica: alg_buy
        [InlineKeyboardButton("✅ LO VOGLIO COMPRARE", callback_data='alg_buy')],
        [InlineKeyboardButton("🔙 Indietro", callback_data='main_start')]
    ]
    
    # Trucco: cancelliamo il vecchio menu per pulizia
    try: await query.message.delete()
    except: pass
        
    await context.bot.send_message(query.message.chat_id, testo, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'alg_buy':
        dati = CATALOGO["anno_1"]["algebra"]
        # CHIAMIAMO UTILS PER CONCLUDERE
        await invia_ordine_generico(
            update, context,
            titolo_materia="Algebra e Geometria",
            dettaglio_ordine="Pacchetto Completo (Unica opzione)",
            prezzo_totale=dati['prezzo']
        )
