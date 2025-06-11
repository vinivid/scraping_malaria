from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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

    ABA_BUSCAR  = 'step1-tab'
    ABA_GRADE   = 'step4-tab' 

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

    def _click_aba(self, nav : Chrome, aba : str) -> None:
        while True:
            try:
                nav.find_element(By.ID, aba).click()
                break
            except ElementClickInterceptedException:
                continue

    def _esperar_carregar(self, nav : Chrome) -> None:
        WebDriverWait(nav, 10).until(
            lambda nav: nav.execute_script("return jQuery.active == 0")
        )
        WebDriverWait(nav, 10).until(ec.invisibility_of_element_located((By.CLASS_NAME, 'blockUI.blockOverlay')))  

    def _checa_erro_popup(self, nav : Chrome) -> bool:    
        self._esperar_carregar(nav)
        try:
            nav.find_element(By.ID, 'err')
            nav.find_elements(By.CLASS_NAME, 'ui-button-text')[2].click()
            return True
        except NoSuchElementException:
            return False

    def _get_curso_info(self, nav : Chrome) -> Tag:    
        self._esperar_carregar(nav)
        return BeautifulSoup(nav.page_source, features="html.parser").find(id='step2')
    
    def _get_disciplinas(self, nav : Chrome) -> tuple[Tag, list[tuple[str, Tag]]]:
        self._esperar_carregar(nav)
        self._click_aba(nav, self.ABA_GRADE)
        self._esperar_carregar(nav)

        tudo_soup = BeautifulSoup(nav.page_source, "html.parser")
        disciplina_tags : list[Tag] = tudo_soup.find_all(class_='disciplina')
        disciplina_e_info : list[tuple[str, Tag]] = []

        for dis in disciplina_tags:
            nav.find_element(By.XPATH, f"//a[@data-coddis='{dis.text}']").click()
            self._esperar_carregar(nav)

            classes_do_bloco = set([
                "ui-dialog",
                "ui-widget",
                "ui-widget-content",
                "ui-corner-all",
                "ui-draggable",
                "ui-resizable"
            ])

            def classes_iguais(tag):
                return (
                    tag.name == 'div' and
                    tag.has_attr('class') and
                    set(tag['class']) == classes_do_bloco
                )

            disciplina_soup : Tag = BeautifulSoup(nav.page_source, "html.parser").find(classes_iguais)
            disciplina_e_info.append((dis.text, disciplina_soup))
            self._esperar_carregar(nav)
            nav.find_element(By.CLASS_NAME, 'ui-icon.ui-icon-closethick').click()

        grade_curricular_soup : Tag = BeautifulSoup(nav.page_source, "html.parser").find(id='step4')

        return (grade_curricular_soup, disciplina_e_info)


    def _ini_chrome(self) -> Chrome:
        options = Options()
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        ChromeDriverManager().install()

        return Chrome(service=Service(ChromeDriverManager().install()),options=options)
    # A função de init é suposta dar scrape em todos os conteudos, inicializando as classes
    # a partir do conteudo scrapado
    def __init__(self):
        self.unidades    = []
        self.cursos      = []
        self.disciplinas = []

        navegador : Chrome = self._ini_chrome()
        CURSOS_URL : str = 'https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275'
        navegador.get(CURSOS_URL)

        unidades = self._get_unidades(navegador)        

        for seletor, unidade in zip(range(2, len(unidades) + 2), unidades):
            seletor_de_unidades = navegador.find_element(By.ID, "comboUnidade")
            seletor_de_unidades.click()
            seletor_de_unidades.find_element(By.CSS_SELECTOR, f'#comboUnidade :nth-child({seletor})').click()

            cursos = self._get_cursos(navegador)

            self.unidades.append(UnidadeUsp(unidade, set(cursos)))

            for seletor_curso, curso in zip(range(2, len(cursos) + 2), cursos):
                seletor_de_cursos = navegador.find_element(By.ID, "comboCurso")
                botao_enviar = navegador.find_element(By.ID, "enviar")
                seletor_de_cursos.click()
                seletor_de_cursos.find_element(By.CSS_SELECTOR, f'#comboCurso :nth-child({seletor_curso})').click()
                botao_enviar.click()

                if not self._checa_erro_popup(navegador):
                    info_curso_soup = self._get_curso_info(navegador)
                    self.cursos.append(CursoUsp(curso, info_curso_soup))

                    pagina_grade_soup, disciplina_e_info = self._get_disciplinas(navegador)

                    self._click_aba(navegador, self.ABA_BUSCAR)
                    
        navegador.close()