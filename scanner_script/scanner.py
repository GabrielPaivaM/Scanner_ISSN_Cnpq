import requests
from bs4 import BeautifulSoup
import csv
from colorama import Fore, init

init(autoreset=True)

url_base = 'https://portal.issn.org/resource/ISSN/'

# Conta qual registro esta sendo verificado.
c = 0

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

# Abre o arquivo em modo leitura para ler os ISSNs.
with open('cnpq_issn_s_not_found.csv', 'r', encoding='UTF-8') as r:
    reader = csv.reader(r)
    issn_s = list(reader)

    if not issn_s:
        print("Não existem ISSNs no arquivo .csv")
    else:
        # Abre o arquivo em modo escrita para sobrescrever o conteúdo já existente, se não tiver um arquivo ele cria um novo.
        with open('cnpq_verify_portal_issn.csv', 'w', newline='', encoding='UTF-8') as f:
            writer = csv.writer(f)
            f.write("Title; ISSN; Language; Country; Subject; Observation;\n")

            for row in issn_s:
                issn = row[0]
                url_page = f'{url_base}{issn}'
                site = requests.get(url_page, headers=headers)
                soup = BeautifulSoup(site.content, 'html.parser')

                # Inicializando as variáveis de saída
                title = "null"
                issn_text = issn
                language = "null"
                country = "null"
                subject = "null"
                obs = "null"

                # Para verificar se a página existe (se o ISSN é válido).
                page_title = soup.find('h3', class_="page-title")

                # Para verificar se o ISSN foi comprimido.
                item_result_title = soup.find('h5', class_="item-result-title")
                # Lista dos possiveis motivos dos registros não estarem disponiveis.
                namelist = ["Suppressed record", "record", "Provisional record", "Cancelled record", "Unreported record", "Awaiting validation record"]

                # Verifica se o registro existe.
                if page_title and page_title.get_text().strip() == "The requested numbers do not correspond to valid ISSNs:":
                    title = "null"
                    language = "null"
                    country = "null"
                    subject = "null"
                    obs = "Registro inexistente"

                # Verifica se o registro existe e foi comprimido.
                elif item_result_title and item_result_title.get_text().strip() in namelist:
                    title = "null"
                    language = "null"
                    country = "null"
                    subject = "null"
                    obs = "Registro encontrado mas sem info"

                # Verifica se existe e não foi comprimido.
                elif item_result_title and not item_result_title.get_text().strip() in namelist:
                    titlen = item_result_title.get_text().strip()

                    # Tira o início inutilizável do titulo.
                    titlem = titlen.replace('Key-title    ', '')
                    titleo = titlem.replace(';', '')
                    title = titleo.replace("'", "")

                    content_divs = soup.find_all('div', class_="item-result-content-text")
                    if content_divs:
                        paragraphs = content_divs[1].find_all('p')
                        if paragraphs:
                            for p in paragraphs:
                                if "Language: " in p.get_text().strip():
                                    language = p.get_text().strip().replace("Language: ", "")
                                if "Country: " in p.get_text().strip():
                                    country = p.get_text().strip().replace("Country: ", "")
                                if "Subject: " in p.get_text().strip():
                                    subject = p.get_text().strip().replace("Subject: ", "")

                    obs = "Registro Encontrado"

                # Escreve a linha no arquivo CSV
                line = f"'{title}'; '{issn}'; '{language}'; '{country}'; '{subject}'; '{obs}';\n"
                f.write(line)
                c += 1

                match obs:
                    case "Registro Encontrado":
                        print(
                            f'{c}{Fore.LIGHTGREEN_EX} Registro {Fore.LIGHTWHITE_EX}{issn}{Fore.LIGHTGREEN_EX} verificado com status: {Fore.LIGHTBLUE_EX}{obs}')
                    case "Registro encontrado mas sem info":
                        print(
                            f'{c}{Fore.LIGHTGREEN_EX} Registro {Fore.LIGHTWHITE_EX}{issn}{Fore.LIGHTGREEN_EX} verificado com status: {Fore.LIGHTYELLOW_EX}{obs}')
                    case "Registro inexistente":
                        print(
                            f'{c}{Fore.LIGHTGREEN_EX} Registro {Fore.LIGHTWHITE_EX}{issn}{Fore.LIGHTGREEN_EX} verificado com status: {Fore.LIGHTRED_EX}{obs}')
