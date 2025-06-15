from bs4 import BeautifulSoup
from bs4.element import Tag
from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys

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
    disciplinas : dict[str, DisciplinaUsp]

    ABA_BUSCAR  = 'step1-tab'
    ABA_GRADE   = 'step4-tab' 

    def _get_unidades(self, nav : Chrome) -> list[str]:
        """
        Pega o nome de todas as unidades presentes no
        seletor de unidades.

        :param nav: O navegador para scraping dos dados. Ele
            já deve estar na aba de carreiras no site do jupiter.
        :type nav: Chrome

        :return: Retorna uma lista contendo o nome de cada
            unidade como uma string.
        :rtype: list[str]
        """
        # Demora um pouco para a lista das unidades aparecerem então é necessario esperar
        WebDriverWait(nav, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#comboUnidade :nth-child(2)")))
        unidades_soup = BeautifulSoup(nav.page_source, features="html.parser")
        return [child.get_text() for child in unidades_soup.find(id='comboUnidade').children 
                if (type(child) is Tag) and child.get('value') != '']

    def _get_cursos(self, nav : Chrome) -> list[str]:
        """
        Pega o nome de todos os cursos presentes no
        seletor de cursos.

        :param nav: O navegador para scraping dos dados. Ele
            já deve ter selecionado e clicado pelo menos uma unidade
            para que o seletor de cursos carregue.
        :type nav: Chrome

        :return: Retorna uma lista contendo o nome de cada
            curso como uma string.
        :rtype: list[str]
        """
        # Novamente é necessario esperar a lista de cursos
        WebDriverWait(nav, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#comboCurso :nth-child(2)")))

        cursos_soup = BeautifulSoup(nav.page_source, features="html.parser")
        return [child.get_text() for child in cursos_soup.find(id='comboCurso') 
                    if (type(child) is Tag) and child.get('value') != '']       

    def _click_aba(self, nav : Chrome, aba : str) -> None:
        """
        Clica eu uma das abas 'buscar', 'informações do curso',
        'projeto pedagógico' ou 'grade curricular'. A tentativa
        de clicar na aba sera infinita até que seja possível 
        clicar.

        :param nav: O navegador para scraping dos dados. Ele
            não pode estar com o popup de erro se não essa função
            ficara infinitamente tentando clicar em uma das abas.
        :type nav: Chrome
        :param aba: Uma string do id da aba ser clicada. Os id seguem 
            o padrão, 'step1-tab', 'step2-tab' ..., dentro dessa classe
            são disponibilizadas duas constantes que já possuem os id's
            das duas abas que serão necessarias clicar.
        :type aba: str
        """
        while True:
            try:
                nav.find_element(By.ID, aba).click()
                break
            except ElementClickInterceptedException:
                continue

    def _esperar_carregar(self, nav : Chrome) -> None:
        """
        Espera o popup de carregar desaparecer.

        :param nav: O navegador para scraping dos dados. Pressupõe
            que o navegador acabou de fazer algo que faz com que
            o popup apareça.
        :type nav: Chrome
        """
        time.sleep(0.1)
        WebDriverWait(nav, 10).until(
            lambda nav: nav.execute_script("return jQuery.active == 0")
        )
        WebDriverWait(nav, 30).until(ec.invisibility_of_element_located((By.CLASS_NAME, 'blockUI.blockOverlay')))  

    def _checa_erro_popup(self, nav : Chrome) -> bool:
        """
        Checa pelo popup de erro (informações não encontradas).
        Se ele for encontrado, fecha ele.

        :param nav: O navegador para scraping dos dados. Pressupõe
            que o navegador acabou de fazer algo que possivelmente
            faça que o popup apareça.
        :type nav: Chrome
        :return: Retorna True se o popup foi encontrado, False caso
            contrario.
        :rtype: bool
        """   
        self._esperar_carregar(nav)
        try:
            nav.find_element(By.ID, 'err')
            nav.find_elements(By.CLASS_NAME, 'ui-button-text')[2].click()
            return True
        except NoSuchElementException:
            return False

    def _get_curso_info(self, nav : Chrome) -> Tag:
        """
        Pega a aba das informações do curso.

        :param nav: O navegador para scraping dos dados. Pressupõe
            que o navegador clicou no botão de enviar após selecionar
            um curso.
        :type nav: Chrome
        :return: Aba de informações para scraping.
        :rtype: Tag
        """      
        self._esperar_carregar(nav)
        return BeautifulSoup(nav.page_source, features="html.parser").find(id='step2')
    
    def _get_disciplinas(self, nav : Chrome) -> tuple[Tag, list[str]]:
        """
        Pega a aba da grade curricular do curso e as informações
        de cada disciplina na grade deste curso caso as informações
        ainda não tenham sido coletadas.

        :param nav: O navegador para scraping dos dados. Pressupõe
            que o navegador clicou no botão de enviar após selecionar
            um curso.
        :type nav: Chrome
        :param dis_ja: O set das disciplinas que ja foram processadas
            para evitar que a mesma aba seja aberta duas vezes.
        :type nav: set[str]
        :return: A função retorna a aba da grade para scraping na primeira
            posição da tupla. Na segunda retorna uma lista com o código de
            cada disciplina da grade do curso.
        :rtype: tuple[Tag, list[str]]
        """     
        self._esperar_carregar(nav)
        self._click_aba(nav, self.ABA_GRADE)
        self._esperar_carregar(nav)

        tudo_soup = BeautifulSoup(nav.page_source, "html.parser")
        disciplinas_do_curso : list[Tag] = tudo_soup.find_all(class_='disciplina')

        grade_curricular_soup : Tag = BeautifulSoup(nav.page_source, "html.parser").find(id='step4')

        return (grade_curricular_soup, disciplinas_do_curso)


    def _ini_chrome(self) -> Chrome:
        """
        Inicializa o webdriver do Chrome. **É necessario que você
        tenha o Chrome instalado no seu computador no caminho padrão.**

        :return: O navegador para webscraping.
        :rtype: Chrome
        """      
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
        self.disciplinas = {}

        navegador : Chrome = Firefox()
        CURSOS_URL : str = 'https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275'
        navegador.get(CURSOS_URL)

        unidades = self._get_unidades(navegador)        

        qtd_unidades = 0
        try:
            numero_de_unidades_para_scrape = int(sys.argv[1])
        except ValueError:
            numero_de_unidades_para_scrape = len(unidades)
            print('\033[0;31mValor passado não é um inteiro valido. Portanto foi escolhido o número máximo de unidades\033[0;37m\n')
        except IndexError:
           numero_de_unidades_para_scrape = len(unidades)

        if numero_de_unidades_para_scrape < 0:
            qtd_unidades = len(unidades)
            print('\033[0;31mNão é possivel fazer o scrape de um número negativo de unidades. Portanto foi escolhido o número máximo de unidades.\033[0;37m\n')
        elif numero_de_unidades_para_scrape > len(unidades):
            qtd_unidades = len(unidades)
            print('\033[0;31mNão é possivel fazer o scrape de mais unidades que as disponiveis no website. Portanto foi escolhido o número máximo de unidades.\033[0;37m\n')
        else:
            qtd_unidades = numero_de_unidades_para_scrape
        
        for seletor, unidade in zip(range(2, qtd_unidades + 2), unidades):
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

                    pagina_grade_soup, disciplinas_do_curso = self._get_disciplinas(navegador)
                    for disciplina in disciplinas_do_curso:
                        if disciplina.text in self.disciplinas:
                            self.disciplinas[disciplina.text].add_curso(curso)
                            continue

                        nova_disciplina = DisciplinaUsp(disciplina, curso)
                        self.disciplinas.update({nova_disciplina.get_codigo() : nova_disciplina})

                    self._click_aba(navegador, self.ABA_BUSCAR)

        navegador.close()