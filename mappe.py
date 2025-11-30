# --- LINK GOOGLE MAPS SPECIFICI ---
LINK_N_M = "https://maps.app.goo.gl/owdmvYHmsW6CeAFp9"       # Incolla qui il link per N/M
LINK_P = "https://maps.app.goo.gl/47DMPgysWgoMu4dJ8"         # Incolla qui il link per P
LINK_T = "https://maps.app.goo.gl/SKQZAZYa3NwMeN717"         # Incolla qui il link per T
LINK_R = "https://maps.app.goo.gl/yZHN8EnBydJ8pEMh6"         # Incolla qui il link per R
LINK_I = "https://maps.app.goo.gl/JVbt67jjjnzKSXvu5"         # Incolla qui il link per I

# Sede Centrale (Cortile/Ingresso principale) - Per aule 1-19, A, B, C, D, S, LAIB
LINK_CENTRALE = "https://maps.app.goo.gl/7WE7rdgcmaCj6Sg17"    # Incolla qui il link del cortile

# Sedi distaccate per gestione errori
LINK_LINGOTTO = "https://maps.app.goo.gl/PuKzsv6yEUniAjvb6"
LINK_MIRAFIORI = "https://maps.app.goo.gl/euYrwHKqLcFAw5wbA"


def get_link_aula(nome_aula):
    """
    Riceve il nome (es. 'Aula 5N', '12I') e restituisce il link Maps all'ingresso migliore.
    """
    nome = nome_aula.upper().strip()
    
    # --- 1. GESTIONE SEDI ESTERNE ---
    if "LINGOTTO" in nome:
        return LINK_LINGOTTO
    if "MIRAFIORI" in nome:
        return LINK_MIRAFIORI

    # --- 2. PADIGLIONI SPECIFICI (CITTADELLA/SUD) ---
    
    # Aule N e M (Passano per N)
    if "N" in nome or "M" in nome:
        # Escludiamo casi strani se ci fossero, ma N e M sono uniche
        return LINK_N_M
        
    # Aule P
    if "P" in nome:
        return LINK_P
        
    # Aule T
    if "T" in nome:
        return LINK_T
        
    # Aule R
    if "R" in nome:
        return LINK_R
        
    # Aule I (Informatica)
    # ATTENZIONE: "LAIB" contiene la lettera "I", ma sono nella sede centrale solitamente.
    # Quindi diamo il link I solo se c'è "I" MA NON c'è "LAIB"
    if "I" in nome and "LAIB" not in nome:
        return LINK_I

    # --- 3. DEFAULT: SEDE CENTRALE (Aule 1, 8, 12A, 5S, LAIB, Sale studio) ---
    # Se non è nessuno dei precedenti, lo mandiamo in Corso Duca
    return LINK_CENTRALE
