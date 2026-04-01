import asyncio
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

#load_dotenv('/etc/secrets/.env')

# Importiamo la logica del tuo bot dalla cartella
from aule_bot import logic as aule_logic
# Quando avrai il secondo bot, lo importerai così:
from appunti_bot import logic as appunti_logic

# Importiamo il worker separato per Oracle Cloud
#from oracle_logic.oracle_cloud_worker import oracle_cloud_worker


# --- SERVER FAKE PER RENDER (Uno solo per tutti!) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Hub Bots Running!")

def start_fake_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

# --- FUNZIONE PRINCIPALE ---
async def main():
    # 1. Avvia il server web in background
    t = threading.Thread(target=start_fake_server)
    t.daemon = True
    t.start()
    print("🌍 Server Hub avviato.")

    # 2. Configura i bot
    print("🤖 Configuro AuleBot...")
    bot_aule = aule_logic.setup_bot()
    
    if not bot_aule:
        print("❌ Impossibile avviare AuleBot (Token?)")
        return

    print("📚 Configuro AppuntiBot...")
    bot_appunti = appunti_logic.setup_bot()
    
    # 3. Avvia i bot in parallelo
    # Usiamo il Context Manager per gestire start/stop pulito
    async with bot_aule, bot_appunti: #<-- aggiungi qui il secondo bot
        
        print("🚀 Avvio Polling AuleBot...")
        
        await bot_aule.start()
        await bot_aule.updater.start_polling()
        
        await bot_appunti.start()
        await bot_appunti.updater.start_polling()


        # Inietta il task Oracle nell'Event Loop
        #print("☁️ Avvio worker Oracle in background...")
        # NOTA: Ora lanciamo la funzione senza passarle bot_aule!
        #asyncio.create_task(oracle_cloud_worker())

        
        print("✅ SISTEMA ONLINE! Premi Ctrl+C per fermare.")
        
        # Mantiene lo script vivo per sempre
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
