#################################
#(Gli attrezzi): Gestisce il JSON delle prese, il Server fantasma per Render e la formattazione del testo.
################################

import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Importiamo il nuovo file mappe
import mappe 

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
def formatta_nome(nome):
    """Aggiunge grassetto, icona presa e LINK preciso"""
    
    # Check Presa
    ha_presa = (nome in AULE_CON_PRESE) or (f"Aula {nome}" in AULE_CON_PRESE)
    
    # Genera Link usando il file mappe.py
    link_maps = mappe.get_link_aula(nome)
    
    if ha_presa:
        return f'<a href="{link_maps}"><b>{nome}</b></a>🔌'
    else:
        return f'<a href="{link_maps}">{nome}</a>'

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
