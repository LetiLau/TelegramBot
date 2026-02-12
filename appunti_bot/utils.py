import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes  # <--- ContextTypes va importato da QUI

# Prende l'ID dalle variabili d'ambiente
ADMIN_ID = os.getenv("ADMIN_ID")

async def invia_ordine_generico(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                titolo_materia: str, 
                                dettaglio_ordine: str, 
                                prezzo_totale: str):
    """
    Funzione universale per chiudere un ordine.
    I parametri devono essere passati dai singoli moduli.
    """
    query = update.callback_query
    user = query.from_user
    
    # 1. Costruzione Messaggio ADMIN
    user_link = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    username = f"@{user.username}" if user.username else "Nessun Username"
    
    msg_admin = (
        f"💰 <b>NUOVO ORDINE: {titolo_materia}</b>\n\n"
        f"👤 <b>Cliente:</b> {user_link} ({username})\n"
        f"📝 <b>Dettaglio:</b> {dettaglio_ordine}\n"
        f"💶 <b>Totale da incassare:</b> {prezzo_totale}\n"
    )
    
    # 2. Tentativo invio ADMIN
    invio_ok = False
    if ADMIN_ID:
        try:
            await context.bot.send_message(ADMIN_ID, msg_admin, parse_mode='HTML')
            invio_ok = True
        except Exception as e:
            print(f"Errore invio admin: {e}")
            invio_ok = False

    # 2. Gestione Messaggio UTENTE (Modificato)
    
    # A. Cancelliamo il menu di acquisto precedente (pulizia)
    # Così l'utente non può cliccare "Compra" due volte per sbaglio
    try:
        await query.message.delete()
    except:
        pass
                                  
    # 3. Risposta UTENTE
    if invio_ok:
        msg_utente = (
            "✅ <b>Richiesta Inviata!</b>\n\n"
            f"Hai scelto: <b>{titolo_materia}</b>\n"
            f"🛒 Versione: {dettaglio_ordine}\n"
            f"💶 Prezzo: <b>{prezzo_totale}</b>\n\n"
            "📩 Il venditore ha ricevuto la notifica e ti scriverà a breve su Telegram."
        )
        # Tasto per tornare alla Home (che gestirà logic.py)
        # B. Bottone SPECIALE per tornare a casa senza cancellare questo messaggio
        kb = [[InlineKeyboardButton("🏠 Torna alla Home", callback_data='return_home_new')]]

        # C. Usiamo send_message invece di edit_message_text
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg_utente, 
            reply_markup=InlineKeyboardMarkup(kb), 
            parse_mode='HTML'
        )

    else:
        # Fallback se il bot non riesce a scriverti
        url_admin = f"tg://user?id={ADMIN_ID}" if ADMIN_ID else "https://t.me/RedzFoxx"
        msg_errore = (
            "❌ <b>Errore tecnico.</b>\n"
            "Non sono riuscito ad avvisare il venditore in automatico.\n"
            "Per favore, scrivigli tu manualmente."
        )
        kb = [[InlineKeyboardButton("💬 Contatta Admin", url=url_admin)]]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg_errore, 
            reply_markup=InlineKeyboardMarkup(kb), 
            parse_mode='HTML'
        )
