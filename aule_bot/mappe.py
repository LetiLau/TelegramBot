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
    Restituisce il link all'ingresso corretto gestendo le eccezioni.
    """
    nome = nome_aula.upper().strip() # Es: "LAIB 1B", "R4B"
    
    # --- 1. GESTIONE SEDI ESTERNE ---
    if "LINGOTTO" in nome: return LINK_LINGOTTO
    if "MIRAFIORI" in nome: return LINK_MIRAFIORI

    # --- 2. GESTIONE CASI SPECIALI (LAIB) ---
    if "LAIB" in nome:
        # Se c'è una T (es: LAIB 1T), va al padiglione T
        if "T" in nome:
            return LINK_T
        
        # Se c'è una B EXTRA oltre a quella della parola LAI(B) (es: LAIB 1B)
        # Contiamo le B: "LAIB 1" ne ha 1. "LAIB 1B" ne ha 2.
        if nome.count("B") > 1:
            return LINK_N_M # Cittadella (M)
            
        # Tutti gli altri LAIB (LAIB 1, LAIB 2...) vanno in centrale
        return LINK_CENTRALE

    # --- 3. PADIGLIONI SPECIFICI ---
    
    # Aule R (R1, R2, R4b...)
    # Basta che ci sia "R" e un numero. "R4B" contiene R.
    if "R" in nome and any(c.isdigit() for c in nome):
        return LINK_R

    # Aule T (1T, 2T...)
    if "T" in nome: 
        return LINK_T

    # Aule N e M (Via Boggio)
    # Escludiamo SALA per sicurezza
    if ("N" in nome or "M" in nome) and "SALA" not in nome:
         return LINK_N_M

    # Aule P
    if "P" in nome: 
        return LINK_P

    # Aule I (Informatica - Sede Sud)
    if "I" in nome:
        return LINK_I

    # --- 4. DEFAULT (Sede Centrale) ---
    # Aule 1, 8, 12A, 5S, Sale Studio...
    return LINK_CENTRALE
