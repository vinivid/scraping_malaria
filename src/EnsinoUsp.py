from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from .UnidadeUsp import UnidadeUsp
from .CursoUsp import CursoUsp
from .DisciplinaUsp import DisciplinaUsp

class EnsinoUsp:
    """
    A classe EnsinoUsp é uma interface para o conjunto de 
    infromações relacionadas aos cursos oferecidos pela USP.
    Permitindo obter informações sobre os institutos, cursos
    oferecidos pelos institutos e sobre disciplinas.
    """

    unidades    : list[UnidadeUsp]
    cursos      : list[CursoUsp]
    disciplinas : list[DisciplinaUsp]

    # A função de init é suposta dar scrape em todos os conteudos, inicializando as classes
    # a partir do conteudo scrapado
    def __init__(self):
        self.unidades    = []
        self.cursos      = []
        self.disciplinas = []

        navegador : webdriver.Firefox = webdriver.Firefox()
        CURSOS_URL : str = 'https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275'
        navegador.get(CURSOS_URL)
        # Demora um pouco para a lista das unidades aparecerem então é necessario esperar
        # TODO: colocar algum tipo de mensagem de erro se isso n carregar, e outras coisas de carregar em geral
        WebDriverWait(navegador, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#comboUnidade :nth-child(2)")))
        seletor_de_cursos = navegador.find_element(By.ID, "comboUnidade")

        cursos_soup = BeautifulSoup(navegador.page_source, features="html.parser")

        cursos_id : Tag = cursos_soup.find(id='comboUnidade')
        unidades = [child.get_text() for child in cursos_id.children 
                    if (type(child) is Tag) and child.get('value') != '']

        for seletor, unidade in zip(range(2, len(unidades) + 2), unidades):
            seletor_de_cursos.click()
            seletor_de_cursos.find_element(By.XPATH, f'//option[{seletor}]').click()
            # Novamente é necessario esperar a lista de cursos
            WebDriverWait(navegador, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#comboCurso :nth-child(2)")))

            cursos_soup = BeautifulSoup(navegador.page_source, features="html.parser")
            cursos = [child.get_text() for child in cursos_soup.find(id='comboCurso') 
                    if (type(child) is Tag) and child.get('value') != '']

            self.unidades.append(UnidadeUsp(unidade, set(cursos)))
            

        navegador.close()