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
            "titolo": "Fisica 1",
            "prezzo": "12,00€",
            "file_demo": "appunti_bot/files/demo_fisica1.pdf",
            
            # --- NUOVI CAMPI ---
            "prof": "Prof. Stefania Bufalino",
            "anno_accademico": "2024/2025",
            "libro": "Mazzoldi, Nigro, Voci - Elementi di Fisica",
            
            # Elenco dei formati (puoi metterne quanti vuoi)
            "formati": [
                "PDF (Indice Cliccabile)",
                "Buono per stampa A4"
            ],

            # Descrizione lunga (HTML)
            "descrizione": """
<b>Appunti completi di teoria ed esercizi.</b>
Ho seguito il corso prendendo appunti su tablet, rielaborando poi a casa con il libro di testo.

📌 <b>Argomenti principali:</b>
• Cinematica del punto e <u>moti relativi</u>.
• Dinamica e forze apparenti.
• Sistemi di punti e Corpo Rigido.
• Termodinamica (fino al 2° principio).

<i>Ottimi per preparare lo scritto.</i>
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
