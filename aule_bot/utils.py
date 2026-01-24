#################################
#(Gli attrezzi): Gestisce il JSON delle prese, il Server fantasma per Render e la formattazione del testo.
################################
import json
import os
from . import mappe 

# --- GESTIONE PERCORSI (FIX PER SOTTOCARTELLE) ---
# Ottiene il percorso assoluto della cartella dove si trova questo file (utils.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'aule_prese.json')
# -------------------------------------------------

# --- 🎨 SEZIONE ESTETICA (MODIFICA QUI) 🎨 ---
ICONA_PRESA = "🔌"           # L'emoji per le prese
ICONA_LINK = ""              # Vuoi un'icona prima del nome? (es. "📍") Lascia vuoto se no.
USA_GRASSETTO_PRESA = True   # True = Grassetto se ha presa. False = Testo normale.
# ---------------------------------------------

# --- GESTIONE FILE JSON ---
AULE_CON_PRESE = set()

def carica_prese():
    global AULE_CON_PRESE
    try:
        # MODIFICA QUI: Usiamo JSON_PATH invece del nome file secco
        with open(JSON_PATH, 'r') as f:
            lista = json.load(f)
            AULE_CON_PRESE = set(lista)
            print(f"✅ Utils: Caricate {len(AULE_CON_PRESE)} aule con prese.")
    except Exception as e:
        print(f"⚠️ Utils: Errore caricamento JSON ({e}). Uso set vuoto.")
        AULE_CON_PRESE = set()

# --- FORMATTAZIONE TESTO ---
def formatta_nome(nome, mostra_icona=True):
    """Applica lo stile definito nella Sezione Estetica in alto"""
    
    # Check Presa
    ha_presa = (nome in AULE_CON_PRESE) or (f"Aula {nome}" in AULE_CON_PRESE)
    link_maps = mappe.get_link_aula(nome)
    
    # Preparo il nome (aggiungo eventuale icona link prima)
    testo_visibile = f"{ICONA_LINK}{nome}"
    
    # Logica Grassetto
    if ha_presa and USA_GRASSETTO_PRESA:
        html = f'<a href="{link_maps}"><b>{testo_visibile}</b></a>'
    else:
        html = f'<a href="{link_maps}">{testo_visibile}</a>'

    # Aggiunta Icona Presa (solo se richiesto e se c'è la presa)
    if ha_presa and mostra_icona:
        return f'{html}{ICONA_PRESA}'
    
    return html

def controlla_presa(nome):
    return (nome in AULE_CON_PRESE) or (f"Aula {nome}" in AULE_CON_PRESE)
