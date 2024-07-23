import requests
from bs4 import BeautifulSoup
import time

import csv

from colorama import Fore, Style, init

url = 'https://portal.issn.org/resource/ISSN/'

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

site = requests.get(url, headers=headers)
soup = BeautifulSoup(site.content, 'html.parser')

# Abre o arquivo em modo leitura para ler os issn's.
with open('cnpq_issn_s_not_found.csv', 'r', encoding='UTF-8') as r:
    reader = csv.reader(r)
    issn_s = list(reader)

    if not issn_s:

        print("Não existem ISSN's no arquivo .csv")        
    
    else:
        # Abre o arquivo em modo escrita para sobrescrever o conteudo ja existente, se não tiver um arquivo ele cria um novo.
        with open('cnpq_verify_portal_issn.csv', 'w', newline='', encoding='UTF-8') as f:

            for issn in issn_s:

                url_page = f'https://portal.issn.org/resource/ISSN/{issn}'
                site = requests.get(url_page, headers=headers)
                soup = BeautifulSoup(site.content, 'html.parser')

                # Para verificar se a pagina existe (se o ISSN é valido).
                page_title = soup.find('h3', class_="page-title")

                # Para verificar se o ISSN foi comprimido.
                title = soup.find('h5', class_="item-result-title")

                title = "-"
                issn_text = issn
                lenguage = "-"
                country = "-"
                subject = "-"
                obs = "-"

                # Verifica se o registro existe.
                if page_title.get_text().strip == "The requested numbers do not correspond to valid ISSNs:":
                    title = "null"
                    issn_text = issn
                    lenguage = "null"
                    country = "null"
                    subject = "null"
                    obs = "Resgistro não existe."
                
                # Verifica se o registro existe e foi comprimido.
                elif title.get_text().strip() == "Suppressed record":
                    title = "null"
                    issn_text = issn
                    lenguage = "null"
                    country = "null"
                    subject = "null"
                    obs = "Resgistro comprimido."

                # Verifica se existe e não foi comprimido.
                elif not title.get_text().strip() == "Suppressed record":
                    title = title.get_text().strip()
                    issn_text = issn
                    
                    content_div = soup.find('div', class_="item-result-content-text")
                    paragraphs = content_div.find_all('p')

                    for p in paragraphs:
                        span = p.find_all('span')

                        lenguage = "null"
                        country = "null"
                        subject = "null"

                        if span[0].get_text().strip == "Language: ":
                            lenguage = p.get_text().strip()
                        
                        if span[0].get_text().strip == "Country: ": 
                            country = p.get_text().strip()
                        
                        if span[0].get_text().strip == "Subject: ": 
                            subject = p.get_text().strip()

                    obs = "Resgistro Encontrado."
                
                line = "Title: " + title + ";" + " " + "ISSN: " + issn_text + ";" + " " + "Language: " + lenguage + ";" + " " + "Language: " + lenguage + ";" + " " + "Subject: " + subject + ";" + "\n"
                        
                f.write(line)

                match obs:
                    case "Resgistro Encontrado.":
                        print(f'{Fore.LIGHTGREEN_EX}Registro {Fore.LIGHTWHITE_EX}{issn}{Fore.LIGHTGREEN_EX} verificado com status: {Fore.LIGHTBLUE_EX}{obs}\n')
                    
                    case "Resgistro comprimido.":
                        print(f'{Fore.LIGHTGREEN_EX}Registro {Fore.LIGHTWHITE_EX}{issn}{Fore.LIGHTGREEN_EX} verificado com status: {Fore.LIGHTYELLOW_EX}{obs}\n')
                    
                    case "Resgistro não existe.":
                        print(f'{Fore.LIGHTGREEN_EX}Registro {Fore.LIGHTWHITE_EX}{issn}{Fore.LIGHTGREEN_EX} verificado com status: {Fore.LIGHTRED_EX}{obs}\n')