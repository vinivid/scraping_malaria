import re

class UnidadeUsp:
    nome : str
    sigla : str
    cursos : set[str]

    def __init__(self, nome : str, cursos : set[str]):
        self.nome = nome
        self.sigla : str = re.findall(r'\(([^\)]+)\)', nome)[0].strip()
        self.cursos = cursos

    #Outros métodos que talvez sejam necessarios