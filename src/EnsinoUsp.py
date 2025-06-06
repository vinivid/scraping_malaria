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

        #Pegando o seletor de unidades e pegando o nome de todas as unidades
        cursos_id : Tag = cursos_soup.find(id='comboUnidade')
        # São todos os cursos no seletor com exceção do curso vazio
        unidades = [child.get_text() for child in cursos_id.children 
                    if (type(child) is Tag) and child.get('value') != '']

        # Esse loop representa clicar em cada elemento. Em XPath o index
        # de um filho começa em 1, então devemos pular o 1 pq ele é o seletor
        # vazio. A quantidade de elementos que terão de ser selecionados
        # é a quantidade de unidades + 2 por causa do elemento vazio ignorado
        # que adiciona 1. E para o loop ser inclusivo e ir até o ultimo elemento 
        for seletor, unidade in zip(range(2, len(unidades) + 2), unidades):
            # Clica na unidade selecionada e espera que os cursos da unidade carreguem
            seletor_de_cursos.click()
            seletor_de_cursos.find_element(By.XPATH, f'//option[{seletor}]').click()
            WebDriverWait(navegador, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#comboCurso :nth-child(2)")))

            # Pega todos os cursos, que é o mesmo seletor das unidades então a mesma lógica
            cursos_soup = BeautifulSoup(navegador.page_source, features="html.parser")
            cursos = [child.get_text() for child in cursos_soup.find(id='comboCurso') 
                    if (type(child) is Tag) and child.get('value') != '']

            # Isso ja informação o suficiente para criar uma unidade            
            self.unidades.append(UnidadeUsp(unidade, set(cursos)))
            

        navegador.close()