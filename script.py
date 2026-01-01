import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

def rodar_automacao():
    url = "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    noticias_lista = []
    artigos = soup.find_all('article', class_='tileItem')

    for item in artigos:
        titulo = item.find('h2').text.strip()
        link = item.find('a')['href']
        info_texto = item.get_text()
        data_encontrada = re.search(r'(\d{2}/\d{2}/\d{4})', info_texto)
        data_pub = data_encontrada.group(1) if data_encontrada else "---"

        txt = titulo.upper()
        if any(w in txt for w in ["IRPF", "LUCROS E DIVIDENDOS", "INSS", "PESSOA FÍSICA"]):
            categoria = "Pessoa Física"
        elif any(w in txt for w in ["ICMS", "PIS", "COFINS", "IRPJ", "CSLL", "SIMPLES NACIONAL", "ISS", "IBS", "CBS", "EMPRESA"]):
            categoria = "Empresarial"
        else:
            categoria = "Geral"

        noticias_lista.append({
            "Data Publicação": data_pub,
            "Interesse": categoria,
            "Título": titulo,
            "Link": link
        })

    df = pd.DataFrame(noticias_lista)
    
    # SALVAR COMO CSV (Mais fácil para o Google Sheets ler)
    df.to_csv("noticias_receita.csv", index=False, encoding='utf-8-sig')
    print("Arquivo CSV atualizado!")

if __name__ == "__main__":
    rodar_automacao()
