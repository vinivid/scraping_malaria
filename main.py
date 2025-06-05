from bs4 import BeautifulSoup
import requests as req
from src.CursosUsp import CursosUsp

def main():
    BeautifulSoup(req.get('https://uspdigital.usp.br/jupiterweb/jupCarreira.jsp?codmnu=8275').text).find()

if __name__ == "__main__":
    main()
