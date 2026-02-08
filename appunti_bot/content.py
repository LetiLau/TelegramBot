# FILE: appunti_bot/content.py

# Dizionario dei testi.
# Qui puoi usare i tag HTML:
# <b>Grassetto</b>
# <i>Corsivo</i>
# <u>Sottolineato</u>
# <a href="http...">Link</a>

CATALOGO = {
    "anno_1": {
        "fisica_1": {
            # --- DATI OBBLIGATORI ---
            "titolo": "⚛️Fisica 1",
            "prezzo": "12,00€",
            "file_demo": "appunti_bot/files/demo_fisica1.pdf",
            
            # --- NUOVI CAMPI ---
            "prof": "Prof. Stefania Bufalino",
            "anno_accademico": "2024/2025",
            "libro": "Mazzoldi, Nigro, Voci - Elementi di Fisica (meccanica e termodinamica)",
            
            # Elenco dei formati (puoi metterne quanti vuoi)
            "formati": [
                "PDF (Indice Cliccabile), colori/bianco e nero",
                "notewise (versione app gratuita Android/IOS), modificabile"
            ],

            # Descrizione lunga (HTML)
            "descrizione": """
Appunti completi di formule, teoria, dimostrazioni e note teoriche per i quiz, completamente sostitutivi alle <b>lezioni di teoria</b>.
Basati sulle slide della professoressa e sul libro di riferimento.
Sono <i>scritti a mano</i> (chiari e leggibili) e <i>colorati</i> per facilitare la comprensione delle note relative agli argomenti/formule, compresi di disegni e immagini.
<b>102 pagine</b>

📌 <b>Argomenti principali:</b>
• Cinematica e dinamica del punto
• Moti relativi
• Sistemi di punti, corpo rigido, urti
• Termodinamica.
• Fluidodinamica
• Gravitazione

"""
        },
        
        "chimica": {
            "titolo": "Chimica",
            "prezzo": "10,00€",
            "file_demo": "appunti_bot/files/demo_chimica.pdf",
            # Se dimentichi prof o anno, il bot non crasherà!
            "formati": ["PDF", "GoodNotes"],
            "descrizione": "Appunti schematici su orbitali, legami e stechiometria."
        },
  
  "anno_2": {

      #altre materie
  
   }
  
}
