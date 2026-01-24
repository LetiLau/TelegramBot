#################################
#(Gli attrezzi): Gestisce il JSON delle prese, il Server fantasma per Render e la formattazione del testo.
################################

import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import mappe 

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
        with open('aule_prese.json', 'r') as f:
            lista = json.load(f)
            AULE_CON_PRESE = set(lista)
            print(f"✅ Utils: Caricate {len(AULE_CON_PRESE)} aule con prese.")
    except Exception as e:
        print(f"⚠️ Utils: Errore JSON ({e}). Uso set vuoto.")
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

# --- SERVER RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Polito Online")

def start_fake_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

def avvia_server_background():
    t = threading.Thread(target=start_fake_server)
    t.daemon = True
    t.start()
