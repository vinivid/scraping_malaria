from bs4.element import Tag

class CursoUsp:
    unidade_responsavel : str
    nome : str 
    disciplinas : dict[str, str]

    def __init__(self, conteudos : Tag) -> None:
        print(conteudos.prettify())


        pass

    #Outros métodos que talvez sejam necessarios