class UnidadeUsp:
    nome : str
    cursos : set[str]

    def __init__(self, nome : str, cursos : set[str]):
        self.nome = nome
        self.cursos = cursos

    #Outros métodos que talvez sejam necessarios