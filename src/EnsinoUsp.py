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
import time
import sys
import timeit
import re
from difflib import get_close_matches

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
    cursos      : dict[str, CursoUsp]
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
        return BeautifulSoup(nav.page_source, features="html.parser").find(id='step4').find('table').find('tr').find('td')
    
    def _get_disciplinas(self, nav : Chrome) -> list[Tag]:
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

        return disciplinas_do_curso

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
    
    def _processar_quantidade_de_unidades(self, quantidade_de_unidades : int) -> int:
        """
        Processa o primeiro argumento do programa, que é a qunatidade
        de unidades para serem scrapadas.

        :param quantidade_de_unidades: É a quantiadade de que estão presentes
            no seletor de unidades, utilizado como valor padrão para entradas
            erroneas ou inexistentes.
        :type quantidade_de_unidades: int
        :return: Quantiadade de unidades para scrape.
        :rtype: int
        """
        try:
            numero_de_unidades_para_scrape = int(sys.argv[1])
        except ValueError:
            print('\033[0;31mValor passado não é um inteiro valido. Portanto foi escolhido o número máximo de unidades\033[0;37m\n')
            return quantidade_de_unidades
        except IndexError:
            return quantidade_de_unidades

        if numero_de_unidades_para_scrape < 0:
            print('\033[0;31mNão é possivel fazer o scrape de um número negativo de unidades. Portanto foi escolhido o número máximo de unidades.\033[0;37m\n')
            return quantidade_de_unidades
        elif numero_de_unidades_para_scrape > quantidade_de_unidades:
            print('\033[0;31mNão é possivel fazer o scrape de mais unidades que as disponiveis no website. Portanto foi escolhido o número máximo de unidades.\033[0;37m\n')
            return quantidade_de_unidades
        else:
            return numero_de_unidades_para_scrape

    # A função de init é suposta dar scrape em todos os conteudos, inicializando as classes
    # a partir do conteudo scrapado
    def __init__(self):
        self.unidades    = []
        self.cursos      = {}
        self.disciplinas = {}

        navegador : Chrome = self._ini_chrome()
        CURSOS_URL : str = 'https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275'
        navegador.get(CURSOS_URL)

        unidades = self._get_unidades(navegador)        

        qtd_unidades = self._processar_quantidade_de_unidades(len(unidades))
        if qtd_unidades == 1:
            print('Fazendo o scrape de 1 unidade da USP')
        else:
            print(f'Fazendo o scrape de {qtd_unidades} unidades da USP')

        tempo_do_inicio = timeit.default_timer()
        
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
                    curso_conteudo = self._get_curso_info(navegador) 
                    novo_curso = CursoUsp(curso, unidade, curso_conteudo)     
                    disciplinas_do_curso = self._get_disciplinas(navegador)

                    for disciplina in disciplinas_do_curso:
                        modalidade = disciplina.parent.parent.parent.find("tr").find("td").text
                    
                        if disciplina.text in self.disciplinas: 
                            self.disciplinas[disciplina.text].add_curso(curso)
                            novo_curso.add_disciplina(modalidade, disciplina.text)
                            continue

                        nova_disciplina = DisciplinaUsp(disciplina, curso)                        
                        self.disciplinas.update({nova_disciplina.get_codigo() : nova_disciplina})

                        novo_curso.add_disciplina(modalidade, disciplina.text)

                    self.cursos.update({curso : novo_curso})
                    self._click_aba(navegador, self.ABA_BUSCAR)
                else:
                    novo_curso = CursoUsp(curso, unidade, None)     
                    self.cursos.update({curso : novo_curso})

        navegador.close()
        tempo_do_fim = timeit.default_timer()
        tempo_em_seg = round(tempo_do_fim - tempo_do_inicio, 2)
        if tempo_em_seg < 60:
            if qtd_unidades == 1:
                print(f'Fim do scrape. 1 unidade scrapada em {tempo_em_seg} segundos\n')
            else:
                print(f'Fim do scrape. {qtd_unidades} unidades scrapadas em {tempo_em_seg} segundos\n')
        else:
            if qtd_unidades == 1:
                print(f'Fim do scrape. 1 unidade scrapada em {int(tempo_em_seg // 60)}min {round(tempo_em_seg - (tempo_em_seg // 60) * 60)}s\n')
            else:
                print(f'Fim do scrape. {qtd_unidades} unidades scrapadas em {int(tempo_em_seg // 60)}min {round(tempo_em_seg - (tempo_em_seg // 60) * 60)}s\n')
        
    def cursos_por_unidade(self):
        """
        Para cada unidade scrapada imprime todos os cursos que ela possui.
        """
        for unidade in self.unidades:
            print(unidade)
    
    def dados_do_curso(self, nome_do_curso : str) -> bool:
        """
        Se o nome do curso passado como argumento estiver presente
        no dicionario de cursos imprime o seu valor e retorna true.
        Caso contrario retorna false.

        :param nome_do_curso: Nome do curso que deve ter seus dados imprimidos.
        :type nome_do_curso: str
        :return: Retorna true caso o curso seja encotrado, false caso contrario.
        :rtype: bool
        """
        if nome_do_curso in self.cursos:
            print(self.cursos[nome_do_curso])
            return True
        
        return False
    
    def dados_de_todos_os_cursos(self):
        """
        Imprime os dados de todos os cursos scrapados.
        """
        for curso in self.cursos.values():
            print(curso)
    
    def dados_da_disciplina_codigo(self, codigo_da_disciplina : str) -> bool:
        """
        Se o codigo da disciplina passada como argumento estiver presente
        no dicionario de disciplina imprime o seu valor e retorna true.
        Caso contrario retorna false.

        :param nome_do_curso: Código da disciplina que deve ter seus dados imprimidos.
        :type nome_do_curso: str
        :return: Retorna true caso a disciplina seja encotrado, false caso contrario.
        :rtype: bool
        """
        if codigo_da_disciplina in self.disciplinas:
            print(self.disciplinas[codigo_da_disciplina])
            return True
        
        return False
    
    def dados_da_disciplina_nome(self, nome : str) -> bool:
        """
        Se o nome da disciplina passada como argumento estiver presente
        no dicionario de disciplina imprime o seu valor e retorna true.
        Caso contrario retorna false.

        :param nome_do_curso: Nome da disciplina que deve ter seus dados imprimidos.
        :type nome_do_curso: str
        :return: Retorna true caso a disciplina seja encotrado, false caso contrario.
        :rtype: bool
        """
        disciplina =  [x for x in self.disciplinas.values() if x.get_nome() == nome]
        if len(disciplina) > 0:
            print(disciplina[0])
            return True
    
        return False
    
    def disciplinas_usadas_em_mais_de_um_curso(self):
        """
        Imprime os dados de todas as disciplinas que sao utilizadas em mais de
        um curso.
        """
        disciplinas = [x for x in self.disciplinas.values() if len(x.get_cursos()) > 1]
        for disciplina in disciplinas:
            print(disciplina)

    def _validar_entrada(self, funcionalidade : str, argumentos : list[str]) -> tuple[bool, str | tuple[int, str]]:
        """
        Checa se, para a funcionalidade dada como argumento,
        existe uma quantidade valida de argumentos. Se tiver retorna
        uma tupla/string desses argumentos, caso contrario retorna 
        uma string de erro para ser imprimida.

        :param funcionalidade: Funcionalidade para validar os argumentos.
        :type funcionalidade: str
        :param argumentos: Argumentos para executar a função.
        :type argumentos: list[str]
        :return: Retorna uma tupla em que a primeira posiçao é um booleano
            indicando se é uma entrada valida (True), se for uma entrada valida
            a segunda posicao sao os argumentos para a funcionalidade. Caso 
            contrario retorna false e a segunda posição é uma string de erro.
        """
        if funcionalidade == 'lc' or funcionalidade == 'ddtc' or funcionalidade == 'ddmc':
            return (True, '')
        elif funcionalidade == 'ddc':
            if len(argumentos) > 1:
                return (True, ' '.join(argumentos[1:]))
            else:
                return (False, "É necessário de um curso para buscar os seus dados. Zero cursos foram passados.")
        elif funcionalidade == 'ddd':
            if len(argumentos) > 2:
                if argumentos[1] == 'cod':
                    return (True, (0, ' '.join(argumentos[2:])))
                else:
                    return (True, (1, ' '.join(argumentos[2:])))
            else:
                return (False, "É necessário de um disciplina e seu nome/códgo para buscar os seus dados. Zero disciplinas foram passados.")
            
            
    def _cursos_ou_disciplinas_proximos_ao_nao_encontrado(self, nome_procurado : str, curso_ou_disciplina : int):
        """
        Imprime no stdout os cursos ou  que sa próximos ao procurado.

        :param nome_procurado: Nome que foi procurado mais não encontrado.
        :type nome_procurado: str
        :param curso_ou_disciplina: 0 se for um curso para verificar a proximidade, e 1 se for uma disciplina.
        """
        if curso_ou_disciplina == 0:
            nomes_proximos = get_close_matches(nome_procurado, [x.get_curso() for x in self.cursos.values()], n=5, cutoff=0.6)
            if len(nomes_proximos) > 0:
                print('Curso não encontrado. Talvez você estava procurando por:')
                for nome in nomes_proximos:
                    print(nome)
            else:
                print('Curso não encontrado.')
        else:
            nomes_proximos = get_close_matches(nome_procurado, [x.get_nome() for x in self.disciplinas.values()], n=5, cutoff=0.6)
            if len(nomes_proximos) > 0:
                print('Disciplina não encontrada. Talvez você estava procurando por:')
                for nome in nomes_proximos:
                    print(nome)
            else:
                print('Disciplina não encontrada.')

    def _print_ajuda(self):
        """
        Imprime as informaçoes das funcionalidades disponiveis.
        """
        print('lc -> (listar cursos) Lista todos os cursos oferecidos pelas unidades scrapadas.')
        print('\tEssa funcinalidade não precisa de argumentos.\n')
        print('ddc -> (dados do curso) Imprime os dados de um determinado curso.')
        print('\tEssa funcinalidade recebe como argumento o nome do curso que deseja saber os dados.')
        print('\tEx: ddc Marketing (Ciclo Básico) - noturno\n')
        print('ddtc -> (dados de todos os cursos) Imprieme os dados de todos os cursos.')
        print('\tEssa funcinalidade não precisa de argumentos.\n')
        print('ddd -> (dados da disciplina) Imprieme os dados da disciplina que deseja saber os dados.')
        print('\tEssa funcinalidade recebe como primeiro argumento se a disciplina sera buscada pod código ou por nome, e como segundo o valor da respectiva escolha.')
        print('\tEx: ddd cod ACH0142\n')
        print('\tEx: ddd nome Sociedade, Multiculturalismo e Direitos - Cultura Digital')
        print('ddmc -> (dados das disciplinas em mais de um curso) Imprime os dados das disciplinas que estão em mais de um curso.')
        print('\tEssa funcinalidade não precisa de argumentos.\n')
        print('ajuda -> Imprime na tela as funcionalidade disponiveis para serem executadas, em conjunto com instruções de como utiliza-las.\n')
        print('sair -> Sai do programa.\n')

    def consulta_de_informacoes(self):
        """
        Faz com que a stdin possa executar consultas
        na classe atraves de inputs especificos.
        """
        funcionalidades = set(['lc', 'ddc', 'ddtc', 'ddd', 'ddmc'])
        print('Consulta de informações scrapadas.\nDigite um funcionalidade para executa-la.\nLista de funcionalidades disponiveis:')
        self._print_ajuda()

        while True:
            entrada_do_usuario = input()
            tokens = re.split(r"\s", entrada_do_usuario)

            if len(tokens) > 0:
                funcionalidade = tokens[0].lower()
                
                if funcionalidade == 'sair':
                    print("Saindo do programa.")
                    return
                elif funcionalidade == 'ajuda':
                    self._print_ajuda()
                elif funcionalidade in funcionalidades:
                    entrada_valida, args = self._validar_entrada(funcionalidade, tokens)

                    if entrada_valida:
                        if funcionalidade == 'lc':
                            self.cursos_por_unidade()
                        elif funcionalidade == 'ddc':
                            print(args)
                            encontrado = self.dados_do_curso(args)
                            if not encontrado:
                                self._cursos_ou_disciplinas_proximos_ao_nao_encontrado(args, 0)
                        elif funcionalidade == 'ddtc':
                            self.dados_de_todos_os_cursos()
                        if funcionalidade == 'ddd':
                            if args[0] == 0:
                                encontrado = self.dados_da_disciplina_codigo(args[1])
                                if not encontrado:
                                    print('Código da disciplina não foi encontrado.')
                            else:
                                encontrado = self.dados_da_disciplina_nome(args[1])
                                if not encontrado:
                                    self._cursos_ou_disciplinas_proximos_ao_nao_encontrado(args, 1)
                        if funcionalidade == 'ddmc':
                            self.disciplinas_usadas_em_mais_de_um_curso()
                    else:
                        print(args)
                else:
                    print("Funcionalidade enviada não existe, tente novamente.")
            else:
                print("É necessario enviar pelo menos uma funcionalidade valida.")