from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
import time

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

    def _get_unidades(self, nav : Chrome) -> list[Tag]:
        # Demora um pouco para a lista das unidades aparecerem então é necessario esperar
        WebDriverWait(nav, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#comboUnidade :nth-child(2)")))
        unidades_soup = BeautifulSoup(nav.page_source, features="html.parser")
        return [child.get_text() for child in unidades_soup.find(id='comboUnidade').children 
                if (type(child) is Tag) and child.get('value') != '']

    def _get_cursos(self, nav : Chrome) -> list[Tag]:
        # Novamente é necessario esperar a lista de cursos
        WebDriverWait(nav, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#comboCurso :nth-child(2)")))

        cursos_soup = BeautifulSoup(nav.page_source, features="html.parser")
        return [child.get_text() for child in cursos_soup.find(id='comboCurso') 
                    if (type(child) is Tag) and child.get('value') != '']       

    def _click_aba_buscar(self, nav : Chrome) -> None:
        while True:
            try:
                nav.find_element(By.ID, 'step1-tab').click()
                break
            except ElementClickInterceptedException:
                continue

    def _checa_erro_popup(self, nav : Chrome) -> bool:
        # Por algum motivo é necessario esperar esse tempo para funcionar
        time.sleep(0.1)
    
        WebDriverWait(nav, 10).until(
            lambda nav: nav.execute_script("return jQuery.active == 0")
        )
        WebDriverWait(nav, 10).until(ec.invisibility_of_element_located((By.CLASS_NAME, 'blockUI blockOverlay')))  
        
        try:
            nav.find_element(By.ID, 'err')
            return False
        except NoSuchElementException:
            return True

    def _get_curso_info(self, nav : Chrome) -> Tag:
        time.sleep(0.1)
    
        WebDriverWait(nav, 10).until(
            lambda nav: nav.execute_script("return jQuery.active == 0")
        )
        WebDriverWait(nav, 10).until(ec.invisibility_of_element_located((By.CLASS_NAME, 'blockUI blockOverlay')))

        return BeautifulSoup(nav.page_source, features="html.parser")

    # A função de init é suposta dar scrape em todos os conteudos, inicializando as classes
    # a partir do conteudo scrapado
    def __init__(self):
        self.unidades    = []
        self.cursos      = []
        self.disciplinas = []

        navegador : Chrome = Chrome()
        CURSOS_URL : str = 'https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275'
        navegador.get(CURSOS_URL)

        unidades = self._get_unidades(navegador)

        # Esse loop percorre cada curso de uma unidade, criando as classes a partir das informações
        # coletadas
        for seletor_unidade, unidade in zip(range(2, len(unidades) + 2), unidades):
            seletor_de_unidades = navegador.find_element(By.ID, "comboUnidade")
            seletor_de_unidades.click()
            seletor_de_unidades.find_element(By.CSS_SELECTOR, f'#comboUnidade :nth-child({seletor_unidade})').click()

            cursos = self._get_cursos(navegador)

            self.unidades.append(UnidadeUsp(unidade, set(cursos)))
            
            # Esse loop acessa cada curso de uma unidade e cria as classes a paritr dessas informações
            for seletor_curso, curso in zip(range(2, len(cursos) + 2), cursos):
                seletor_de_cursos = navegador.find_element(By.ID, "comboCurso")
                botao_enviar = navegador.find_element(By.ID, "enviar")
                seletor_de_cursos.click()
                seletor_de_cursos.find_element(By.CSS_SELECTOR, f'#comboCurso :nth-child({seletor_curso})').click()
                botao_enviar.click()

                if not self._checa_erro_popup(navegador):
                    info_curso_soup = self._get_curso_info(navegador)
                    self.cursos.append(CursoUsp(curso, info_curso_soup.find(id='step2')))

                    self._click_aba_buscar(navegador)
                    
        navegador.close()