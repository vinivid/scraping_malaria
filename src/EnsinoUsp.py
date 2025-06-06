from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from UnidadeUsp import UnidadeUsp
from CursoUsp import CursoUsp
from DisciplinaUsp import DisciplinaUsp

class EnsinoUsp:
    """
    A classe EnsinoUsp é uma interface para o conjunto de 
    infromações relacionadas aos cursos oferecidos pela USP.
    Permitindo obter informações sobre os institutos, cursos
    oferecidos pelos institutos e sobre disciplinas.
    """

    unidades : dict[str, UnidadeUsp]
    cursos : dict[str, CursoUsp]
    disciplinas : dict[str, DisciplinaUsp]

    # A função de init é suposta dar scrape em todos os conteudos, inicializando as classes
    # a partir do conteudo scrapado
    def __init__(self):
        navegador : webdriver.Chrome = webdriver.Chrome()
        CURSOS_URL : str = 'https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275'
        navegador.get(CURSOS_URL)
        # Demora um pouco para a lista das unidades aparecerem então é necessario esperar
        # TODO: colocar algum tipo de mensagem de erro se isso n carregar, e outras coisas de carregar em geral
        WebDriverWait(navegador, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#comboUnidade :nth-child(3)")))

        cursos_html = navegador.page_source
        cursos_soup = BeautifulSoup(cursos_html, features="html.parser")

        cursos_id : Tag = cursos_soup.find(id='comboUnidade')
        for child in cursos_id.children:
            print(child)

        navegador.close()