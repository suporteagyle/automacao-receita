import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def rodar_automacao():
    # Lista de URLs para paginação
    urls = [
        "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias",
        "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias?b_start:int=30",
        "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias?b_start:int=60",
        "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias?b_start:int=90"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    noticias_lista = []

    # Loop para percorrer cada link da lista
    for url in urls:
        print(f"Coletando dados de: {url}")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status() # Verifica se houve erro na requisição
            soup = BeautifulSoup(response.text, 'html.parser')
            
            artigos = soup.find_all('article', class_='tileItem')

            for item in artigos:
                titulo = item.find('h2').text.strip()
                link = item.find('a')['href']
                info_texto = item.get_text()
                
                # Extração da data
                data_encontrada = re.search(r'(\d{2}/\d{2}/\d{4})', info_texto)
                data_pub = data_encontrada.group(1) if data_encontrada else "---"

                # Lógica de categorização
                txt = titulo.upper()
                if any(w in txt for w in ["IRPF", "LUCROS E DIVIDENDOS", "INSS", "PESSOA FÍSICA"]):
                    categoria = "Pessoa Física"
                elif any(w in txt for w in ["ICMS", "PIS", "COFINS", "IRPJ", "CSLL", "SIMPLES NACIONAL", "ISS", "IBS", "CBS", "ESOCIAL", "EMPRESA"]):
                    categoria = "Empresarial"
                else:
                    categoria = "Geral"

                noticias_lista.append({
                    "Data Publicação": data_pub,
                    "Interesse": categoria,
                    "Título": titulo,
                    "Link": link
                })
        except Exception as e:
            print(f"Erro ao acessar {url}: {e}")

    # Criar DataFrame com todos os resultados acumulados
    if noticias_lista:
        df = pd.DataFrame(noticias_lista)
        
        # Remove duplicatas (caso uma notícia apareça em duas páginas)
        df = df.drop_duplicates(subset=['Link'])
        
        # Salva o CSV
        df.to_csv("noticias_receita.csv", index=False, encoding='utf-8')
        print(f"Sucesso! {len(df)} notícias salvas em noticias_receita.csv")
    else:
        print("Nenhuma notícia encontrada.")

if __name__ == "__main__":
    rodar_automacao()
