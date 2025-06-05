from bs4 import BeautifulSoup
import requests as re

class CursosUsp:
    def __init__(self) -> None:
        CARREIRAS_URL : str = 'https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275'    
        carreira_resp = re.get(CARREIRAS_URL)
        carreira_resp.raise_for_status()

        carreiras_soup : BeautifulSoup = BeautifulSoup(carreira_resp.text)
        carreiras_soup.find(id='comboUnidade')
        print(carreiras_soup)