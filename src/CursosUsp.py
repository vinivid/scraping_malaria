from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

class CursosUsp:
    def __init__(self) -> None:
        CURSOS_URL : str = 'https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275'
        navegador : webdriver.Firefox = webdriver.Firefox()
        navegador.get(CURSOS_URL)
        WebDriverWait(navegador, 60).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#comboUnidade :nth-child(3)")))

        cursos_html = navegador.page_source
        cursos_soup = BeautifulSoup(cursos_html, features="html.parser")

        cursos_id : Tag = cursos_soup.find(id='comboUnidade')
        for child in cursos_id.children:
            print(child)

        navegador.close()