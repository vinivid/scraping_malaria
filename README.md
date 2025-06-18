Como instalar o programa:

No seu enviroment de python (venv ou outro similar) e na mesma pasta do arquivo
pyproject.toml execute o seguinte comando:

python3 -m pip install .

Que todas as bibliotecas, assim como a versão do python, serão instaladas.

Para rodar o programa é necessario executar o seguinte comando:

python3 main.py

Se você rodar o programa sem nenhum argumento o programa fara o scrape de todas
as unidades da usp. Caso queira fazer o scrape em um número especifico de unidades 
basta executar:

python3 main.py n

Em que n é a quantidade de unidades desejadas para o scrape.

Funcionalidades disponiveis no programa:

Após os dados terem sidos scrapados as seguintes funcionalidades estarão disponíveis
para serem executadas atraves da stdin:

lc -> (listar cursos) Lista todos os cursos oferecidos pelas unidades scrapadas.
    Essa funcinalidade não precisa de argumentos.

ddc -> (dados do curso) Imprime os dados de um determinado curso.
    Essa funcinalidade recebe como argumento o nome do curso que deseja saber os dados
    Ex: ddc Marketing (Ciclo Básico) - noturno

ddtc -> (dados de todos os cursos) Imprieme os dados de todos os cursos
    Essa funcinalidade não precisa de argumentos.

ddd -> (dados da disciplina) Imprieme os dados da disciplina que deseja saber os dados.
    Essa funcinalidade recebe como primeiro argumento se a disciplina sera buscada pod código ou por nome, e como segundo o valor da respectiva escolha.
    Ex: ddd cod ACH0142\n
    Ex: ddd nome Sociedade, Multiculturalismo e Direitos - Cultura Digital

ddmc -> (dados das disciplinas em mais de um curso) Imprime os dados das disciplinas que estão em mais de um curso.
    Essa funcinalidade não precisa de argumentos.

ajuda -> Imprime na tela as funcionalidade disponiveis para serem executadas, em conjunto com instruções de como utiliza-las.

sair -> Sai do programa.