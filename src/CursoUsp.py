from bs4.element import Tag

class CursoUsp:

    nome : str 
    unidade : str
    dur_idl : str
    dur_min : str
    dur_max : str
    disciplinas_obrigatorias  : set[str]
    disciplinas_opt_livre     : set[str] 
    disciplinas_opt_eletivas  : set[str]

    def __init__(self, curso : str, unidade : str, conteudos : Tag) -> None:
        self.unidade = unidade
        self.nome = curso

        if conteudos is None:
            self.dur_idl = "N/A"
            self.dur_min = "N/A"
            self.dur_max = "N/A"

        else:
            self.dur_idl = conteudos.find("span", class_= "duridlhab").text
            if not self.dur_idl:
                self.dur_idl = "N/A"
                
            self.dur_min = conteudos.find("span", class_= "durminhab").text
            if not self.dur_min:
                self.dur_min = "N/A"
                
            self.dur_max = conteudos.find("span", class_= "durmaxhab").text
            if not self.dur_max:
                self.dur_max = "N/A"

        self.disciplinas_obrigatorias  = set()
        self.disciplinas_opt_livre     = set()
        self.disciplinas_opt_eletivas  = set()
    
    def add_disciplina(self, modalidade: str, disciplina : str) -> None:
        tipo_de_modalidade = modalidade.split(' ')[-1].strip().lower()
        if "obrigatórias" == tipo_de_modalidade:
            self.disciplinas_obrigatorias.add(disciplina)

        elif "livres" == tipo_de_modalidade:
            self.disciplinas_opt_livre.add(disciplina)
            
        elif "eletivas" == tipo_de_modalidade:
            self.disciplinas_opt_eletivas.add(disciplina)

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
        if len(self.disciplinas_obrigatorias) == 0:
            curso_str += "\tN/A\n"
        else:
            for disc in self.disciplinas_obrigatorias:
                curso_str += f'\t{disc}\n'

        curso_str += "\nDisciplinas Optativas Livres:\n"
        if len(self.disciplinas_opt_livre) == 0:
            curso_str += '\tN/A\n'
        else:
            for disc in self.disciplinas_opt_livre:
                curso_str += f'\t{disc}\n'

        curso_str += "\nDisciplinas Optativas Eletivas:\n"
        if len(self.disciplinas_opt_eletivas) == 0:
            curso_str += '\tN/A\n'
        else:
            for disc in self.disciplinas_opt_eletivas:
                curso_str += f'\t{disc}\n'
            
        return curso_str