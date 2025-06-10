from bs4.element import Tag

class CursoUsp:
    unidade_responsavel : str
    nome : str 
    disciplinas : dict[str, str]

    def __init__(self, curso : str, conteudos : Tag) -> None:
        with open(f'{curso}.html', 'w', encoding='utf-8') as fw:
            fw.write(conteudos.prettify())


        pass

    #Outros métodos que talvez sejam necessarios