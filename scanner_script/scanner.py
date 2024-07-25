import sys

import requests
from bs4 import BeautifulSoup
import csv
from colorama import Fore, init

init(autoreset=True)

option = input(f'{Fore.LIGHTWHITE_EX}Deseja forçar atualização? (y/n) ')

url_base = 'https://portal.issn.org/resource/ISSN/'

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

if len(sys.argv) == 2 or len(sys.argv) >= 4:
    print("Digite dqual linha deve começar a ler e em qual deve terminar")
    sys.exit(1)

# Abre o arquivo em modo leitura para ler os ISSNs.
def vefify_if_exist(issn, founds):
    for found in founds:
        if (issn + '\n') == found:
            return True
    return False


with open('cnpq_issn_s_not_found.csv', 'r', encoding='UTF-8') as r:
    reader = csv.reader(r)
    issn_s = list(reader)

    start_line = 0
    end_line = 0

    if len(sys.argv) == 1:
        start_line = 1
        end_line = len(issn_s)

    if len(sys.argv) == 3:
        start_line = int(sys.argv[1])
        end_line = int(sys.argv[2])

    # Conta qual registro esta sendo verificado.
    c = start_line - 1

    if not issn_s:
        print("Não existem ISSNs no arquivo .csv")
    else:

        # Abre o arquivo em modo escrita para sobrescrever o conteúdo já existente, se não tiver um arquivo ele cria um novo.
        if option == 'y' or option == 'Y':
            with open('cnpq_verified_portal_issn.csv', 'w', newline='', encoding='UTF-8') as f:

                for i in range(start_line - 1, end_line):
                    if i >= len(issn_s):
                        print("Linha fora do intervalo.")
                        break

                    issn = issn_s[i][0]
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
                        title = titlen.replace('Key-title    ', '')
                        subjectn = ''

                        content_divs = soup.find_all('div', class_="item-result-content-text")
                        if content_divs:
                            paragraphs = content_divs[1].find_all('p')
                            if paragraphs:
                                for p in paragraphs:
                                    span = p.find('span')
                                    if span:
                                        if "Language:" == span.get_text().strip():
                                            language = p.get_text().strip().replace("Language: ", "")
                                        if "Country:" == span.get_text().strip():
                                            country = p.get_text().strip().replace("Country: ", "")
                                        if "Subject:" == span.get_text().strip():
                                            # Formata
                                            subjectlist = list()
                                            subjectlist.append(f'{p.get_text().strip().replace("Subject: ", "")},')
                                            for str in subjectlist:
                                                subjectn = subjectn + f'{str} '
                                            subject = subjectn[:-2]

                        obs = "Registro Encontrado"

                    # Escreve a linha no arquivo CSV
                    line = f"{title}§ {issn}§ {language}§ {country}§ {subject}§ {obs}§\n"
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

        # Vai salvar somente o que não estiver salvo.
        if option == 'n' or option == 'N':

            for i in range(start_line - 1, end_line):

                with open('cnpq_issn_s_found.csv', 'r', newline='', encoding='UTF-8') as found_read:
                    founds = list(found_read)
                    issn = issn_s[i][0]

                    if not vefify_if_exist(issn, founds):
                        with open('cnpq_verified_portal_issn.csv', 'a', newline='', encoding='UTF-8') as f:
                            if i >= len(issn_s):
                                print("Linha fora do intervalo.")
                                break

                            issn = issn_s[i][0]
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
                            namelist = ["Suppressed record", "record", "Provisional record", "Cancelled record",
                                        "Unreported record", "Awaiting validation record"]

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
                                title = titlen.replace('Key-title    ', '')
                                subjectn = ''

                                content_divs = soup.find_all('div', class_="item-result-content-text")
                                if content_divs:
                                    paragraphs = content_divs[1].find_all('p')
                                    if paragraphs:
                                        for p in paragraphs:
                                            span = p.find('span')
                                            if span:
                                                if "Language:" == span.get_text().strip():
                                                    language = p.get_text().strip().replace("Language: ", "")
                                                if "Country:" == span.get_text().strip():
                                                    country = p.get_text().strip().replace("Country: ", "")
                                                if "Subject:" == span.get_text().strip():
                                                    # Formata
                                                    subjectlist = list()
                                                    subjectlist.append(f'{p.get_text().strip().replace("Subject: ", "")},')
                                                    for str in subjectlist:
                                                        subjectn = subjectn + f'{str} '
                                                    subject = subjectn[:-2]

                                obs = "Registro Encontrado"

                            # Escreve a linha no arquivo CSV
                            line = f"{title}§ {issn}§ {language}§ {country}§ {subject}§ {obs}§\n"
                            f.write(line)
                            c += 1

                            with open('cnpq_issn_s_found.csv', 'a', newline='', encoding='UTF-8') as found_write:
                                found_write.write(f'{issn}\n')
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

                    else:
                        c += 1
                        print(
                            f'{Fore.LIGHTWHITE_EX}{c}{Fore.LIGHTGREEN_EX} Registro {Fore.LIGHTWHITE_EX}{issn}{Fore.LIGHTGREEN_EX} verificado com status: {Fore.LIGHTCYAN_EX}Já registrado')