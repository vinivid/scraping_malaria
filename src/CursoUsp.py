from DisciplinaUsp import DisciplinaUsp
from UnidadeUsp import UnidadeUsp

class CursoUsp:
    unidade_responsavel : UnidadeUsp
    nome : str 
    disciplinas : dict[str, DisciplinaUsp]

    def __init__(self) -> None:
        pass

    #Outros métodos que talvez sejam necessarios