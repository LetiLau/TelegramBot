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
            #"tipo": "standard",
            
            "prezzo": "12,00€",       # Prezzo base (Solo Appunti)

    # togliere commento
            #"prezzo_full": "16,00€",  # NUOVO: Prezzo Pacchetto Completo
            
            "file_demo": "appunti_bot/files/demo-fisica1.pdf",
            
            # --- NUOVI CAMPI ---
            "prof": "Prof. Stefania Bufalino",
            "anno_accademico": "2024/2025",
            "libro": "Mazzoldi, Nigro, Voci - Fisica Vol. I Meccanica e Termodinamica",
            
            # Elenco dei formati (puoi metterne quanti vuoi)
            "formati": [
                "PDF (indice cliccabile), colori/bianco e nero",
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

👇 <b>SCEGLI LA TUA VERSIONE:</b>
1️⃣ <b>Solo appunti </b> di teoria
2️⃣ <b>Pacchetto FULL:
    </b>Include anche vari file di scansione di risoluzione di temi d'esame (Bufalino), formulario pronto all'uso.

"""
    #toglli N/D per pacchetto FULL
        }, #fine fisica 1



        
        "chimica": {
            "titolo": "🧪 Chimica",
            "file_demo": "appunti_bot/files/demo-chimica14.pdf",

            # --- PREZZI E CONFIGURAZIONE ---
            "prezzo_singolo": 1.0,      # Prezzo numerico (float) per i calcoli
            "prezzo_full": "10,00€",    # Testo per il pacchetto completo
            "max_files": 21,            # Numero massimo di capitoli (per fare i bottoni)
            # -------------------------------

            "prof": "Prof. Marco Armandi",
            "anno_accademico": "2024/2025",
            "libro": "Silberberg - Chimica. La natura molecolare della materia e delle sue trasformazioni",
            
            # Se dimentichi prof o anno, il bot non crasherà!
            "formati": [
                "PDF non modificabile (colori o bianco e nero)", 
                "Notewise (versione app gratuita Android/IOS), modificabile"
            ],

            "lista_capitoli": """
• 1, 2, 3 - Materia / Modello Atomico / Teorie Atomiche
• 4, 5 - Numeri quantici e orbitali / Configurazione elettronica
• 6, 7 - Proprietà periodiche e legame ionico / Legame covalente
• 8, 9 - Formule di struttura / Teoria VSEPR
• 10 - Orbitali, legame metallico e forze intermolecolari
• 11, 12, 13 - Gas / Stato liquido e diagrammi di fase / Soluzioni
• 14, 15, 16 - Lo stato solido / Termochimica / Cinetica chimica
• 17, 18 - Equilibrio chimico / Teorie acido base e PH
• 19 - Equilibri e soluzioni acquose
• 20, 21 - Elettrochimica / Chimica Organica
"""
            
            "descrizione": """
Appunti completamente sostitutivi alle <b>lezioni di teoria</b>. 
Basati sulle slide, videolezioni del professore e sul libro di riferimento.
Sono <i>scritti a mano</i> (chiari e leggibili), organizzati in <i>singoli file</i> (in media 5-10 pagine) uno per ogni blocco di slide.
<b>Disponibili fino alla lezione 14</b> (successive presto in arrivo).

📌 <b>Argomenti: (con riferimento ai singoli file):</b>"""

            
        }, #fine chimica


        
        "algebra-geometria": {
            "titolo": "📐Algebra Lineare e Geometria",
            "prezzo": "4,00€",
            "file_demo": "appunti_bot/files/demo-algebra_geometria.pdf",

            "prof": "Prof Giovanni Manno",
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

<i>Scritti a mano</i> in calligrafia chiara e leggibile, colorati, comprensivi dei <u>codici</u> da usare per gli esercizi al computer.
Acquistabili come intero pacchetto.

"""
            
        }, #fine algebra
        
  }, #fine anno 1

    
 
    "anno_2": {
    
      "elettrom_elettrotec": {
            # --- DATI OBBLIGATORI ---
            "titolo": "⚡🧲 Elettromagnetismo e Teoria dei circuiti",
            #"tipo": "standard",
            "file_demo": "appunti_bot/files/demo-elettromag_elettrotec.pdf",
            "prezzo_completo": "14,00€",
            "libri_full": "Mazzoldi, Nigro, Voci - Fisica Vol. II Elettromagnetismo e onde\nYoung, Freedman, Ford - Principi di Fisica Vol 2 Elettromagnetismo e Ottica\nPerfetti - Circuiti elettrici",
            "anno_accademico": "2025/2026",
    
        
            # Elenco dei formati full (puoi metterne quanti vuoi)
            "formati_full": [
                "PDF, colori/bianco e nero",
                "Notewise (versione app gratuita Android/IOS), modificabile",
                "Samsung Notes",
                "Markdown"
            ],

            # Descrizione lunga (HTML)
            "descrizione_full": """

📌Include l'intero corso diviso nei due moduli ufficiali. 
Comprende teoria fisica 2, regole e teoria elettrotecnica, svolgimento esericizi d'esame di fisica 2 (elenco nel dettaglio di fisica), svolgimenti prove d'esame di elettrotecnica.
✅ <b>Modulo Elettrotecnica:</b>
Circuiti fondamentali / partitori / analisi nodale / amplificatori operazionali / Millman / Thevenin / Norton / principio sostituzione / circuiti RL, RC, del secondo ordine / fasori / potenze / Bode.
✅ <b>Modulo Fisica 2:</b>
Elettrostatica (lavoro ed energia, potenziale, forze, campo elettrico, conduttori) / Gauss / eqauzioni di Maxwell / corrente elettrica / magnetostatica / legge di Ampère / Biot-Savart / campi elettrici e magnetici variabili nel tempo / onde elettromagnetiche

Per i dettagli specifici vedere la descrizione dei singoli pacchetti.

""",            

            # --- SOTTO-MODULO 1: ELETTROTECNICA ---
            "mod_elettro": {
                "nome": "⚡ Elettrotecnica",
                "prof": "Prof. Paolo Stefano Crovetti",
                "prezzo": "8,00€",
                "libro": "Perfetti - Circuiti elettrici",
                "formati": [
                    "PDF non modificabile (colori o bianco e nero)", 
                    "Notewise (versione app gratuita Android/IOS), modificabile"
                ],
                "descrizione": """

Appunti <b>scritti a mano</b> <i>chiari, leggibili e colorati</i> per facililatare la comprensione. Basati sulle <u>lezioni</u> del professore e sulle <u>slide</u> del corso.
Contengono tutte le <u>formule da usare</u> (applicando i teoremi), note teoriche di precisazione

📌 <b>Argomenti trattati:</b>
• Elenco di regole generali per l'analisi dei circuiti
• Convenzioni sui circuiti / leggi di Kirchhoff / potenza assorbita e generata / energia assorbita da un dipolo
• Leggi di ohm
• Generatori ideali indipendenti e dipendenti / bipoli equivalenti per generatori reali
• Connessione di bipoli / equivalenete di più generatori
• Metodo dei nodi con genetaori corrente e tensione / gestione di un supernodo / metodo del tableau (matrici)
• Partitori di tensione e corrente / teorema di Tellegen / principio sovrapposizione degli effetti / principio di sostituzione
• Amplificatori operazionali
• Teoremi di Millman / Thevenin / Norton
• Metodo del pilota e del generatore di prova
• Condensatori / induttori / circuiti RC e RL / metodo sistematico / circuiti del secondo ordine
• Generatori sinusoidali / fasori / potenza attiva, reattiva, apparente, complessa
• Funzioni di trasferimento / (teoria dei filtri) / diagrammi di Bode

"""
            },

            # --- SOTTO-MODULO 2: FISICA 2 ---
            "mod_fisica2": {
                "nome": "🧲 Fisica 2",
                "prof": "Prof. Mauro Giorcelli",
                "prezzo_base": "1,00€",
                "prezzo_full": "8,00€",
                "libro": "Mazzoldi, Nigro, Voci - Fisica Vol. II Elettromagnetismo e onde\nYoung, Freedman, Ford - Principi di Fisica Vol 2 Elettromagnetismo e Ottica",
                "formati": ["PDF non modificabile", "Notewise (versione app gratuita Android/IOS), modificabile", "Samsung Notes modificabile", "Markdown modificabile"],
                "descrizione": """

Gli appunti di <i>teoria di Fisica 2</i> (senza dimostrazioni) sono stati generati da IA basandosi sulle slide del professore, <u>motivo per cui il loro prezzo è estremamente ridotto</u>. 
Tuttavia sono stati completamente <b>ricorretti e modificati da me</b> con aggiunta di <u>dettagli, note teoriche per i quiz e immagini dei libri</u>.
Sono scritti in formato .md (markdown, ovvero file di testo formattato) e disponibili anche in PDF.
(Visto che sono molto <u>completi ho pensato di metterli comunque a disposizione</u>)

Gli <i>esercizi</i> invece sono quelli che poi possono uscire all'esame (aggiornati all'a.a. specificato) e sono <b>completamente riscritti e risvolti a mano da me</b> (scritti a <i>colori su tablet per facilitare comprensione</i>). 
Sono tratti dal libro Mazzoldi.

📌 <b>Argomenti: (con riferimento ai singoli capitoli):</b>
• 1, 2, 3, 4 - Processi di carica / Coulomb e campo elettrico / Linee di forza / Lavoro e potenziale / Gradiente, rotore, divergenza / Gauss / Condensatori
• 6 - Modello di conduzione della corrente / Legge di Ohm e Resistenze / Potenza elettrica, Effetto Joule e densità di potenza
• 7, 8 - Campo Magnetico / forza magnetica / sorgenti del campo / legge di Ampère
• 10 - Legge di Faraday-Neumann-Lenz / legge di Felici / induttanza / circuiti RL (transitori) / energia magnetica e densità di energia / mutua induzione / corrente di spostamento / equazioni di Maxwell in forma integrale e locale
• 12 - Onde elettromagnetiche: Differenze tra onde elastiche ed elettromagnetiche / velocità della luce / relazione tra i moduli dei campi e propagazione nella materia (indice di rifrazione) / vettore di Poynting / densità di energia / intensità / pressione di radiazione / polarizzazione, legge di Malus, circolare ed ellittica / vettore d'onda / radiazione e resistenza di radiazione.

✏️ <b>Elenco degli esercizi:</b>
Tratti dal libro Mazzoldi con riferimento ai capitoli (nota: potrebbero variare in base all'edizione)
• 1 - 2, 3, 8
• 2 - 1, 5, 7
• 3 - 2, 3, 5, 9
• 4 - 1, 5
• 7 - 1, 4, 6, 7, 10, 11, 12, 13, 9
• 8 - 1, 2, 3, 4, 6, 7, 8, 10, 11, 12
• 10 - 1, 2, 4, 6, 7, 9, 12, 13, 15, 16, 21, 23
• 13 - 2, 3, 4, 5, 8, 9
                
                """
            } #fine fisica 2
          
        }, #fine elettorm elettrotec




        
      
      #altre materie
  
   }
  
}
