###################################
#scraper.py (L'operaio): Si occupa solo di collegarsi al sito SWAS e scaricare i dati grezzi.
###################################

import requests
import re
from bs4 import BeautifulSoup

def scarica_dati_swas():
    """
    Restituisce un dizionario:
    { "14:30-16:00": ["Aula 1", "Aula 3"], ... }
    """
    url = "https://www.swas.polito.it/dotnet/orari_lezione_pub/ricercaaulelibereperfasceorarie.aspx"
    headers = { "User-Agent": "Mozilla/5.0" }
    
    dati_orari = {} 
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200: return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        aule_spans = soup.find_all('span', id=re.compile("lbl_AuleLibere"))

        for span_aula in aule_spans:
            testo_aule = span_aula.text.strip()
            if not testo_aule: continue

            # Trova orario risalendo alla riga
            riga_padre = span_aula.find_parent('tr')
            if riga_padre:
                celle = riga_padre.find_all('td')
                if celle:
                    orario = celle[0].text.strip()
                    
                    # Pulizia lista
                    lista_sporca = testo_aule.split(',')
                    lista_pulita = [a.strip() for a in lista_sporca if a.strip()]
                    
                    dati_orari[orario] = lista_pulita
                    
        return dati_orari

    except Exception as e:
        print(f"❌ Errore scraping: {e}")
        return None
