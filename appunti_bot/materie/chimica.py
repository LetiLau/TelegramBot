import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from appunti_bot.content import CATALOGO
from appunti_bot.utils import invia_ordine_generico

# Chiavi catalogo
KEY_ANNO = "anno_1"
KEY_MATERIA = "chimica"

# Prefisso callback (ch_ = chimica)
PREFIX = "ch_" 

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """MENU PRINCIPALE: Scelta tra pacchetto full o singoli."""
    query = update.callback_query
    
    try: dati = CATALOGO[KEY_ANNO][KEY_MATERIA]
    except: await query.answer("Errore dati", show_alert=True); return

    # --- INVIO DEMO (Standard) ---
    file_path = dati.get("file_demo", "")
    try: await query.message.delete()
    except: pass 

    if os.path.exists(file_path):
        msg_wait = await context.bot.send_message(query.message.chat_id, "⏳ <i>Invio demo...</i>", parse_mode='HTML')
        try:
            with open(file_path, 'rb') as f:
                await context.bot.send_document(chat_id=query.message.chat_id, document=f, caption=f"📄 <b>Anteprima: {dati.get('titolo')}</b>", parse_mode='HTML')
            try: await msg_wait.delete()
            except: pass
        except: pass
    else:
        await query.answer("⚠️ Demo non disponibile", show_alert=True)

    # --- TESTO ---
    p_full = dati.get("prezzo_full", "10€")
    p_sing = dati.get("prezzo_singolo", 1.0)

    # Formattazione lista formati
    formati = dati.get('formati', [])
    formati_txt = "\n".join([f"- {f}" for f in formati])

    anno = dati.get('anno_accademico', 'N/D')
    libro = dati.get('libro', 'N/D')

    prof = dati.get('prof', 'N/D')
    
    testo = (
        f"<b>{dati.get('titolo')}</b>\n"
        f"👤 {prof} (a.a. {anno})\n\n"
        f"📚 Libro di riferimento: {libro}\n"
        f"{dati.get('descrizione')}\n"
        f"{dati.get('lista_capitoli', "<u>Elenco non disponibile</u>")}"
        f"💾 <b>Formati disponibili:</b>\n{formati_txt}\n\n"
        f"💰 Prezzo per singolo file: <b>{p_sing}€</b>\n"
        f"💰 Prezzo per tutti i file: <b>{p_full}</b>\n\n"
        "👇 <b>Come vuoi acquistarli?</b>"
    )
    
    # --- BOTTONI SCELTA ---
    kb = [
        [InlineKeyboardButton(f"📦 Compra TUTTI ({p_full})", callback_data=f'{PREFIX}buy_all')],
        [InlineKeyboardButton(f"📝 Scegli Capitoli ({p_sing}€ cad.)", callback_data=f'{PREFIX}sel_start')],
        [InlineKeyboardButton("🔙 Indietro", callback_data=f'selAnno_{KEY_ANNO}')]
    ]
    
    await context.bot.send_message(chat_id=query.message.chat_id, text=testo, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')


# --- LOGICA SELEZIONE CAPITOLI ---

async def menu_selezione(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra la griglia numerica per selezionare i file."""
    query = update.callback_query
    dati = CATALOGO[KEY_ANNO][KEY_MATERIA]
    max_files = dati.get("max_files", 21)
    
    # Recuperiamo la lista dei selezionati dalla memoria utente
    # Usiamo una chiave univoca per l'utente: carrello_chimica
    user_key = f"cart_{query.from_user.id}_chimica"
    if user_key not in context.user_data:
        context.user_data[user_key] = [] # Inizializza lista vuota
        
    selezionati = context.user_data[user_key] # Es: [1, 5, 10]
    
    # --- COSTRUZIONE GRIGLIA PULSANTI ---
    keyboard = []
    row = []
    for i in range(1, max_files + 1):
        # Se il numero è selezionato, metti la spunta
        label = f"✅ {i}" if i in selezionati else f"{i}"
        # Callback: ch_toggle_5
        row.append(InlineKeyboardButton(label, callback_data=f"{PREFIX}toggle_{i}"))
        
        # Vai a capo ogni 4 numeri
        if len(row) == 4:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row) # Aggiungi l'ultima riga se incompleta

    # --- CALCOLO PREZZO ---
    prezzo_cad = dati.get("prezzo_singolo", 1.0)
    totale = len(selezionati) * prezzo_cad
    
    # Tasto Conferma o Avviso
    if selezionati:
        btn_txt = f"✅ CONCLUDI ORDINE ({totale:.2f}€)"
        callback = f"{PREFIX}confirm"
    else:
        btn_txt = "Scegli almeno un capitolo..."
        callback = "ignore" # Non fa nulla
        
    keyboard.append([InlineKeyboardButton(btn_txt, callback_data=callback)])
    keyboard.append([InlineKeyboardButton("🔙 Annulla", callback_data=f"open_{KEY_ANNO}_{KEY_MATERIA}")]) # Torna al menu chimica

    # --- RECUPERO LA LEGENDA ---
    legenda = dati.get("lista_capitoli", "Elenco non disponibile")

    # --- CREAZIONE MESSAGGIO CON ELENCO ---
    testo = (
        "📝 <b>Selezione Capitoli</b>\n\n"
        f"{legenda}\n"  # <--- Ecco la lista stampata!
        "------------------------------\n"
        "👇 <b>Clicca sui numeri per selezionarli:</b>\n"
        f"💰 Totale attuale: <b>{totale:.2f}€</b>"
    )
    
    # Modifichiamo il messaggio esistente per non fare spam
    try:
        await query.edit_message_text(text=testo, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    except:
        pass # Ignora errore se il messaggio è identico (nessun cambiamento)

async def toggle_capitolo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aggiunge o rimuove un numero dalla memoria."""
    query = update.callback_query
    # ch_toggle_5 -> prendiamo solo "5"
    numero = int(query.data.split("_")[-1])
    
    user_key = f"cart_{query.from_user.id}_chimica"
    if user_key not in context.user_data:
        context.user_data[user_key] = []
        
    lista = context.user_data[user_key]
    
    if numero in lista:
        lista.remove(numero) # Deseleziona
    else:
        lista.append(numero) # Seleziona
        
    context.user_data[user_key] = lista # Salva
    
    # Ricarica il menu (così si aggiornano le spunte e il prezzo)
    await menu_selezione(update, context)


# --- HANDLER PRINCIPALE ---

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce tutti i click di Chimica."""
    query = update.callback_query
    data = query.data
    dati = CATALOGO[KEY_ANNO][KEY_MATERIA]
    
    # 1. COMPRA TUTTO
    if data == f'{PREFIX}buy_all':
        await invia_ordine_generico(
            update, context,
            titolo_materia=dati.get('titolo'),
            dettaglio_ordine="📦 PACCHETTO COMPLETO (Tutti i capitoli)",
            prezzo_totale=dati.get("prezzo_full")
        )
        
    # 2. INIZIA SELEZIONE
    elif data == f'{PREFIX}sel_start':
        await menu_selezione(update, context)
        
    # 3. CLICCA NUMERO (Toggle)
    elif data.startswith(f'{PREFIX}toggle_'):
        await toggle_capitolo(update, context)
        
    # 4. CONFERMA SELEZIONE
    elif data == f'{PREFIX}confirm':
        user_key = f"cart_{query.from_user.id}_chimica"
        selezionati = sorted(context.user_data.get(user_key, []))
        
        prezzo_cad = dati.get("prezzo_singolo", 1.0)
        totale = len(selezionati) * prezzo_cad
        
        # Creiamo la lista leggibile "1, 2, 5"
        lista_txt = ", ".join(map(str, selezionati))
        
        await invia_ordine_generico(
            update, context,
            titolo_materia=dati.get('titolo'),
            dettaglio_ordine=f"📝 Capitoli scelti: {lista_txt}",
            prezzo_totale=f"{totale:.2f}€"
        )
        # Puliamo la memoria dopo l'ordine
        context.user_data[user_key] = []
        
    elif data == 'ignore':
        await query.answer("Seleziona qualcosa prima!")
