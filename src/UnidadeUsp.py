import re

class UnidadeUsp:
    """
    A classe UnidadeUsp representa uma unidade da USP.
    Ela contem o nome da unidade, a sigla da unidade
    e os cursos que essa unidade possui.
    """
    nome : str
    sigla : str
    cursos : set[str]

    def __init__(self, nome : str, cursos : set[str]):
        self.nome = nome
        self.sigla : str = re.findall(r'\(([^\)]+)\)', nome)[0].strip()
        self.cursos = cursos

    def get_nome(self) -> str:
        """
        Pega a string do nome da unidade.

        :return: Nome da unidade.
        :rtype: str
        """
        return self.nome
    
    def get_sigla(self) -> str:
        """
        Pega a string da sigla da unidade.

        :return: Sigla da unidade.
        :rtype: str
        """
        return self.sigla
    
    def get_cursos(self) -> set[str]:
        """
        Pega o conjunto dos nomes dos cursos que
        pertencem a unidade.

        :return: Conjunto de nomes de cursos.
        :rtype: set[str]
        """
        return self.cursos
    
    def get_cursos_str(self) -> str:
        """
        Retorna uma representação legivel dos cursos
        pertencentes a unidade.

        :return: Uma string que contem os cursos da unidade
            e um indicador de qual unidade eles pertencem.
        :rtype: str
        """
        str_cursos = f'Cursos da {self.sigla}:\n'
        for curso in self.cursos:
            str_cursos += f'\t{curso}\n'

        return str_cursos
    
    def __str__(self) -> str:
        unidade_str = f'\n{self.nome}\n'
        unidade_str += self.get_cursos_str()
        return unidade_str