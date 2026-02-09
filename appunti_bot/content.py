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
            "titolo": "⚛️ Fisica 1",
            "tipo": "standard",
            "prezzo": "12,00€",
            "file_demo": "appunti_bot/files/demo_fisica1.pdf",
            
            # --- NUOVI CAMPI ---
            "prof": "👤 Prof. Stefania Bufalino",
            "anno_accademico": "2024/2025",
            "libro": "Mazzoldi, Nigro, Voci - Elementi di Fisica (meccanica e termodinamica)",
            
            # Elenco dei formati (puoi metterne quanti vuoi)
            "formati": [
                "PDF (Indice Cliccabile), colori/bianco e nero",
                "Notewise (versione app gratuita Android/IOS), modificabile"
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
• Termodinamica
• Fluidodinamica
• Gravitazione

"""
        }, #fine fisica 1
        
        "chimica": {
            "titolo": "🧪 Chimica",
            #"prezzo": "10,00€",
            "file_demo": "appunti_bot/files/demo_chimica.pdf",

            "prof": "👤 Prof. Marco Armandi",
            "anno_accademico": "2024/2025",
            "libro": "Silberberg - Chimica. La natura molecolare della materia e delle sue trasformazioni",
            
            # Se dimentichi prof o anno, il bot non crasherà!
            "formati": [
                "PDF non modificabile (colori o bianco e nero)", 
                "Notewise (versione app gratuita Android/IOS), modificabile"
            ],
            
            "descrizione": """
Appunti completamente sostitutivi alle <b>lezioni di teoria</b>. 
Basati sulle slide, videolezioni del professore e sul libro di riferimento.
Sono <i>scritti a mano</i>, organizzati in <i>singoli file</i> (in media 5-10 pagine) uno per ogni blocco di slide.
Disponibili fino alla lezione 14 (successive presto in arrivo).

📌 <b>Argomenti principali (con riferimento ai file):</b>
• 1, 2, 3 - Materia, Modello Atomico, Teorie Atomiche
• 4, 5 - Numeri quantici e orbitali, Configurazione elettronica
• 6, 7 - Proprietà periodiche e legame ionico, Legame covalente
• 8, 9 - Formule di struttura, Teoria VSEPR
• 10 - Orbitali legame metallico forze intermolecolari
• 11, 12, 13 - Gas, Stato liquido e diagrammi di fase, Soluzioni
• 14, 15, 16 - Lo stato solido, Termochimica, Cinetica chimica
• 17, 18 - Equilibrio chimico, Teorie acido base e PH
• 19 - Equilibri e soluzioni acquose
• 20, 21 - Elettrochimica, Chimica Organica

<b>💰 1,00 € cadauno</b>
<b>💰 Tutti 10,00€</b>

"""
        }, #fine chimica

        "algebra-geometria": {
            "titolo": "📐Algebra Lineare e Geometria",
            "prezzo": "5,00€",
            "file_demo": "appunti_bot/files/demo_algebra_geometria.pdf",

            "prof": "👤 Prof Giovanni Manno",
            "anno_accademico": "2024/2025",

            "formati": [
                "PDF non modificabile (colori o bianco e nero)",
                "Samsung Notes modificabile"
            ],

            "descrizione": """
📌 Schemi riassuntivi:
• per volgimento dei quiz esame scritto (5 pagine)
• con formulari e metodi risolutivi (24 pagine)
• comandi matlab (6 pagine + file al computer con i codici)

<i>Scritti a mano</i>, colorati, comprensivi dei codici da usare per gli esercizi al computer.
Acquistabili come intero pacchetto.

"""
            
        }, #fine algebra
        
  }, #fine anno 1
        
  
  "anno_2": {

      #altre materie
  
   }
  
}
