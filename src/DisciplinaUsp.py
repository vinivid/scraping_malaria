class DisciplinaUsp:

    codigo : str
    nome : str
    cred_aula : int
    cred_trab : int
    CH : int
    CE : int
    CP : int
    ATPA : int

    #Perguntar dps pro jiboia! n entendi como eu vou receber os parametros, como vai ser a chamada  da func na """"main""""
    def __init__(self):
        pass

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

    def get_creditos_aula(self) -> int:
        """
        Pega o inteiro de créditos aula da disciplina.

        :return: Créditos aula da disciplina.
        :rtype: int
        """
        return self.cred_aula

    def get_creditos_trabalho(self) -> int:
        """
        Pega o inteiro de créditos trabalho da disciplina.

        :return: Créditos trabalho da disciplina.
        :rtype: int
        """
        return self.cred_trab

    def get_carga_horaria(self) -> int:
        """
        Pega o inteiro de carga horária da disciplina.

        :return: Carga Horária da disciplina.
        :rtype: int
        """
        return self.CH

    def get_carga_horaria_estagio(self) -> int:
        """
        Pega o inteiro de carga horária de estágio da disciplina.

        :return: Carga Horária de Estágio da disciplina.
        :rtype: int
        """
        return self.CE

    def get_carga_horaria_praticas_componentes_curriculares(self) -> int:
        """
        Pega o inteiro de carga horária de práticas como componentes curriculares da disciplina.

        :return: Carga Horária de Práticas Como Componentes Curriculares da disciplina.
        :rtype: int
        """
        return self.CP
    
    def get_atividades_teorico_praticas_aprofundamento(self) -> int:
        """
        Pega o inteiro de ativides teórico práticas de aprofundamento da disciplina.

        :return: Atividades Teórico-Práticas de Aprofundamento da disciplina.
        :rtype: int
        """
        return self.ATPA

    def __str__(self) -> str:
        disciplina_str = f'\nCódigo: {self.codigo}'
        disciplina_str += f'\nNome: {self.nome}'
        disciplina_str += f'\nCréditos Aula: {self.cred_aula}'
        disciplina_str += f'\nCréditos Trabalho: {self.cred_trab}'
        disciplina_str += f'\nCarga Horária: {self.CH}'
        disciplina_str += f'\nCarga Horária Estágio: {self.CE}'
        disciplina_str += f'\nCarga Horária PCC: {self.CP}'
        disciplina_str += f'\nAtividades TPA: {self.ATPA}\n'
        return disciplina_str