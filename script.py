import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

def rodar_automacao():
    # 1. LISTA DE LINKS (Adicione ou remova links aqui)
    links = [
        "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias",
        "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias?b_start:int=30",
        "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias?b_start:int=60",
        "https://www.gov.br/receitafederal/pt-br/assuntos/noticias/ultimas-noticias?b_start:int=90"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    noticias_totais = []

    print(f"⏳ Iniciando coleta de {len(links)} fontes...")

    for url in links:
        try:
            print(f"Lendo: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # O padrão 'tileItem' funciona para a maioria dos sites GOV.BR
            artigos = soup.find_all('article', class_='tileItem')

            for item in artigos:
                titulo = item.find('h2').text.strip()
                link_original = item.find('a')['href']
                
                # Garante que o link seja completo
                link_completo = link_original if link_original.startswith('http') else f"https://www.gov.br{link_original}"
                
                info_texto = item.get_text()
                data_encontrada = re.search(r'(\d{2}/\d{2}/\d{4})', info_texto)
                
                # Adicionamos a aspa simples para o Excel/Sheets não converter em número
                data_pub = f"'{data_encontrada.group(1)}" if data_encontrada else "---"

                # Lógica de Categorização (Agyle BPO)
                txt = titulo.upper()
                if any(w in txt for w in ["IRPF", "LUCROS E DIVIDENDOS", "INSS", "PESSOA FÍSICA"]):
                    categoria = "Pessoa Física"
                elif any(w in txt for w in ["ICMS", "PIS", "COFINS", "IRPJ", "CSLL", "SIMPLES NACIONAL", "ISS", "IBS", "CBS", "eSocial", "EMPRESA"]):
                    categoria = "Empresarial"
                else:
                    categoria = "Geral"

                noticias_totais.append({
                    "Fonte": url.split('/')[2], # Extrai o domínio do site (ex: gov.br)
                    "Data Publicação": data_pub,
                    "Interesse": categoria,
                    "Título": titulo,
                    "Link": link_completo
                })
        except Exception as e:
            print(f"Erro ao ler {url}: {e}")

    # 2. CRIAR TABELA ÚNICA
    df = pd.DataFrame(noticias_totais)
    
    # 3. SALVAR EM CSV
    df.to_csv("noticias_receita.csv", index=False, encoding='utf-8-sig')
    print(f"✅ Sucesso! {len(df)} notícias consolidadas no arquivo.")

if __name__ == "__main__":
    rodar_automacao()
