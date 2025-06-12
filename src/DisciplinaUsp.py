class DisciplinaUsp:

    codigo : str
    nome : str
    cred_aula : int
    cred_trab : int
    carg_h : int
    carg_h_est : int
    carg_h_pcc : int
    att_tpa: str

    #sta_no_curso : dict[str, str] aparentemente essa informação n eh relevante para a diciplina, segundo a malaria

    #Perguntar dps pro jiboia! n entendi como eu vou receber os parametros, como vai ser a chamada  da func na """"main""""
    def __init__(self):
        pass

    def get_codigo(self) -> str:
        return self.codigo

    def get_nome(self) -> str:
        return self.nome

    def get_creditos_aula(self) -> int:
        return self.cred_aula

    def get_creditos_trabalho(self) -> int:
        return self.cred_trab

    def get_carga_horaria(self) -> int:
        return self.carg_h

    def get_carga_horaria_estagio(self) -> int:
        return self.carg_h_est

    def get_carga_horaria_praticas_componentes_curriculares(self):
        return self.carg_h_pcc
    
    #ainda n entendi oq eh isso na real
    def get_atividades_teorico_praticas_aprofundamento(self):
        return self.att_tpa

    def __str__(self) -> str:
        disciplina_str = f'\nCódigo: {self.codigo}'
        disciplina_str += f'\nNome: {self.nome}'
        disciplina_str += f'\nCréditos Aula: {self.cred_aula}'
        disciplina_str += f'\nCréditos Trabalho: {self.cred_trab}'
        disciplina_str += f'\nCarga Horária: {self.carg_h}'
        disciplina_str += f'\nCarga Horária Estágio: {self.carg_h_est}'
        disciplina_str += f'\nCarga Horária PCC: {self.carg_h_pcc}'
        #eu preciso entender esse campo
        disciplina_str += f'\n{self.att_tpa}\n'
        return disciplina_str