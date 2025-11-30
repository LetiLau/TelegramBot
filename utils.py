#################################
#(Gli attrezzi): Gestisce il JSON delle prese, il Server fantasma per Render e la formattazione del testo.
################################

import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

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
        print(f"⚠️ Utils: Errore caricamento JSON ({e}). Uso set vuoto.")
        AULE_CON_PRESE = set()

# --- FORMATTAZIONE TESTO ---
def formatta_nome(nome):
    """Aggiunge grassetto e icona se l'aula ha la presa"""
    # Controlla sia "1" che "Aula 1"
    ha_presa = (nome in AULE_CON_PRESE) or (f"Aula {nome}" in AULE_CON_PRESE)
    
    if ha_presa:
        return f"<b>{nome}</b>🔌"
    return nome

def controlla_presa(nome):
    """Restituisce True se l'aula ha la presa"""
    return (nome in AULE_CON_PRESE) or (f"Aula {nome}" in AULE_CON_PRESE)

# --- SERVER PER RENDER (Keep-Alive) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Polito Online")

def start_fake_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"🌍 Server Fake avviato su porta {port}")
    server.serve_forever()

def avvia_server_background():
    t = threading.Thread(target=start_fake_server)
    t.daemon = True
    t.start()
