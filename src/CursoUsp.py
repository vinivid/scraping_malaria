from bs4.element import Tag
from DisciplinaUsp import DisciplinaUsp

class CursoUsp:

    nome : str 
    unidade : str
    dur_idl : str
    dur_min : str
    dur_max : str
    LDO  : dict[str, DisciplinaUsp] #Lista de Disciplinas Obrigatórias
    LDOL : dict[str, DisciplinaUsp] #Lista de Disciplinas Optativas Livres
    LDOE : dict[str, DisciplinaUsp] #Lista de Disciplinas Optativas Eletivas

    def __init__(self, curso : str, conteudos : Tag) -> None:
        self.unidade = conteudos.find("span", class_="unidade").text
        self.nome = curso

        self.dur_idl = conteudos.find("span", class_= "duridlhab").text
        if not self.dur_idl:
            self.dur_idl = "N/A"
            
        self.dur_min = conteudos.find("span", class_= "durminhab").text
        if not self.dur_min:
            self.dur_min = "N/A"
            
        self.dur_max = conteudos.find("span", class_= "durmaxhab").text
        if not self.dur_max:
            self.dur_max = "N/A"

        # Inicializa os dicionários
        LDO = {}
        LDOL = {}
        LDOE = {}
    
    def set_disciplina(self, modalidade: str, disciplina: DisciplinaUsp) -> None:
        chave = disciplina.get_codigo()

        if "obrigatória" in modalidade.lower():
            self.LDO[chave] = disciplina

        elif "livre" in modalidade.lower():
            self.LDOL[chave] = disciplina
            
        elif "eletiva" in modalidade.lower():
            self.LDOE[chave] = disciplina

    def get_curso(self) -> str:
        """
        Pega a string do nome do curso.

        :return: Nome do curso.
        :rtype: str
        """
        return self.nome

    def get_unidade(self) -> str:
        """
        Pega a string do nome da unidade que fornece o cruso.

        :return: Nome da unidade e sua sigla.
        :rtype: str
        """
        return self.unidade
    
    def get_duracao_ideal(self) -> int:
        """
        Pega o inteiro da duração ideal do curso.

        :return: Duração ideal.
        :rtype: int
        """
        return self.dur_idl
    
    def get_duracao_minima(self) -> int:
        """
        Pega o inteiro da duração minima do curso.

        :return: Duração minima.
        :rtype: int
        """
        return self.dur_min


    def get_duracao_maxima(self) -> int:
        """
        Pega o inteiro da duração maxima do curso.

        :return: Duração maxima.
        :rtype: int
        """
        return self.dur_max
    

    def __str__(self) -> str:
        curso_str = f'\nUnidade: {self.unidade}'
        curso_str += f'\nCurso: {self.nome}'
        curso_str += f'\nDuração Ideal: {self.dur_idl}'
        curso_str += f'\nDuração Mínima: {self.dur_min}'
        curso_str += f'\nDuração Máxima: {self.dur_max}'

        curso_str += "\n\nDisciplinas Obrigatórias:\n"
        for disc in self.LDO.values():
            curso_str += f'{str(disc)}\n'

        curso_str += "\nDisciplinas Optativas Livres:\n"
        for disc in self.LDOL.values():
            curso_str += f'{str(disc)}\n'

        curso_str += "\nDisciplinas Optativas Eletivas:\n"
        for disc in self.LDOE.values():
            curso_str += f'{str(disc)}\n'
        return curso_str

    #Que tal um método para listar todas as disciplinas de um curso?
    #Outros métodos que talvez sejam necessarios