from bs4.element import Tag

class DisciplinaUsp:

    codigo : str
    nome : str
    cred_aula : str
    cred_trab : str
    CH : str
    CE : str
    CP : str
    ATPA : str
    cursos : list[str]

    def __init__(self, tag : Tag, curso : str):
        self.codigo = tag.text
        if not self.codigo:
            self.codigo = "N/A"
        tag = tag.parent.parent
        self.nome = tag.contents[1].text
        if not self.nome:
            self.nome = "N/A"
        self.cred_aula = tag.contents[2].text
        if not self.cred_aula:
            self.cred_aula = "N/A"
        self.cred_trab = tag.contents[3].text
        if not self.cred_trab:
            self.cred_trab = "N/A"
        self.CH = tag.contents[4].text
        if not self.CH:
            self.CH = "N/A"
        self.CE = tag.contents[5].text
        if not self.CE:
            self.CE = "N/A"
        self.CP = tag.contents[6].text
        if not self.CP:
            self.CP = "N/A"
        self.ATPA = tag.contents[7].text
        if not self.ATPA:
            self.ATPA = "N/A"
        self.cursos = []
        self.cursos.append(curso)
        

    def add_curso(self, curso : str) -> None:
        """
        Adiciona um curso na disciplina, indicando que ela faz parte desse curso
        """
        self.cursos.append(curso)

    def get_codigo(self) -> str:
        """
        Pega a string do código da disciplina.

        :return: Código da disciplina.
        :rtype: str
        """
        return self.codigo

    def get_nome(self) -> str:
        """
        Pega a string do nome da disciplina.

        :return: Nome da disciplina.
        :rtype: str
        """
        return self.nome

    def get_creditos_aula(self) -> str:
        """
        Pega o inteiro de créditos aula da disciplina.

        :return: Créditos aula da disciplina.
        :rtype: int
        """
        return self.cred_aula

    def get_creditos_trabalho(self) -> str:
        """
        Pega o inteiro de créditos trabalho da disciplina.

        :return: Créditos trabalho da disciplina.
        :rtype: int
        """
        return self.cred_trab

    def get_carga_horaria(self) -> str:
        """
        Pega o inteiro de carga horária da disciplina.

        :return: Carga Horária da disciplina.
        :rtype: int
        """
        return self.CH

    def get_carga_horaria_estagio(self) -> str:
        """
        Pega o inteiro de carga horária de estágio da disciplina.

        :return: Carga Horária de Estágio da disciplina.
        :rtype: int
        """
        return self.CE

    def get_carga_horaria_praticas_componentes_curriculares(self) -> str:
        """
        Pega o inteiro de carga horária de práticas como componentes curriculares da disciplina.

        :return: Carga Horária de Práticas Como Componentes Curriculares da disciplina.
        :rtype: int
        """
        return self.CP
    
    def get_atividades_teorico_praticas_aprofundamento(self) -> str:
        """
        Pega o inteiro de ativides teórico práticas de aprofundamento da disciplina.

        :return: Atividades Teórico-Práticas de Aprofundamento da disciplina.
        :rtype: int
        """
        return self.ATPA

    def get_cursos(self) -> list[str]:
        """
        Pega uma lista dos cursos que tem essa disciplina como parte da grade curricular.

        :return: Lista dos cursos que tem essa disciplina.
        :rtype: list[str]
        """
        return self.cursos

    def __str__(self) -> str:
        disciplina_str = f'\nCódigo: {self.codigo}'
        disciplina_str += f'\nNome: {self.nome}'
        disciplina_str += f'\nCréditos Aula: {self.cred_aula}'
        disciplina_str += f'\nCréditos Trabalho: {self.cred_trab}'
        disciplina_str += f'\nCarga Horária: {self.CH}'
        disciplina_str += f'\nCarga Horária Estágio: {self.CE}'
        disciplina_str += f'\nCarga Horária PCC: {self.CP}'
        disciplina_str += f'\nAtividades TPA: {self.ATPA}'
        disciplina_str += "\nCursos do qual faz parte:\n"
        for curso in self.cursos:
            disciplina_str += f'\t{curso}\n'
        return disciplina_str