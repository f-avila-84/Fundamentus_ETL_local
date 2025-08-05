import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import unicodedata
import concurrent.futures
import random
import logging
from datetime import datetime # Usaremos datetime para o timestamp local

# --- Configuração de Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Iniciando a coleta de dados fundamentalistas do Fundamentus...")

BASE_URL = "http://www.fundamentus.com.br/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# --- Função auxiliar para normalizar strings (remove acentos, caracteres diacríticos, espaços extras, etc.) ---
def normalize_string_for_comparison(s: str) -> str:
    # REMOVE O CARACTERE '?' INICIAL SE EXISTIR
    if s.startswith('?'):
        s = s[1:]
    # Remove acentos e caracteres diacríticos
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8').strip()
    # Troca espaços não quebráveis por espaços normais
    s = s.replace('\xa0', ' ').strip()
    # Remove múltiplos espaços e garante um único espaço entre as palavras
    s = ' '.join(s.split())
    return s

# --- LISTAS RAW: Strings EXATAS como aparecem no site (antes de remover ':') ---
STRING_FIELDS_RAW = [
    "Tipo:",
    "Empresa:",
    "Setor:",
    "Subsetor:",
    "Data últ cot:", 
    "Últ balanço processado:", 
]

SPECIAL_METRICS_RAW = [
    "Receita Líquida:",
    "EBIT:",
    "Lucro Líquido:",
    "Result Int Financ:",
    "Rec Serviços:",
]

# --- NORMALIZAÇÃO DAS LISTAS UMA ÚNICA VEZ NO INÍCIO DO SCRIPT ---
STRING_FIELDS = [normalize_string_for_comparison(s.replace(":", "")) for s in STRING_FIELDS_RAW]
SPECIAL_METRICS = [normalize_string_for_comparison(s.replace(":", "")) for s in SPECIAL_METRICS_RAW]

# --- Lista de colunas que devem ser convertidas para DATE no SQL Server ---
# Estes são os nomes das colunas APÓS a limpeza por clean_column_name
DATE_COLUMNS_TO_CONVERT = [
    "data_ult_cot",
    "ult_balanco_processado"
]

def clean_and_convert_value(value_str):
    """
    Limpa e converte uma string para um valor numérico (float),
    tratando moedas, porcentagens e separadores decimais.
    """
    if isinstance(value_str, (int, float)):
        return value_str
    
    value_str = str(value_str).strip() # Garante que é string
    value_str = value_str.replace("R\$", "").replace("%", "").replace(".", "").replace(",", ".").strip()
    
    try:
        float_val = float(value_str)
        return float_val
    except ValueError:
        return pd.NA

# 1) Alterar os nomes das colunas para retirar os caracteres especiais
def clean_column_name(col_name: str) -> str:
    """
    Limpa o nome de uma coluna, removendo acentos, caracteres especiais,
    substituindo espaços por underscores e convertendo para minúsculas.
    """
    # Normaliza caracteres Unicode (ex: 'ç' -> 'c', 'é' -> 'e')
    cleaned_name = unicodedata.normalize('NFKD', col_name).encode('ascii', 'ignore').decode('utf-8')
    # Substitui espaços e hifens por underscores
    cleaned_name = cleaned_name.replace(' ', '_').replace('-', '_')
    # Remove qualquer caractere que não seja letra, número ou underscore
    cleaned_name = re.sub(r'[^a-zA-Z0-9_]', '', cleaned_name)
    # Remove underscores duplicados ou no início/fim
    cleaned_name = re.sub(r'_+', '_', cleaned_name).strip('_')
    # Converte para minúsculas
    cleaned_name = cleaned_name.lower()
    return cleaned_name

def scrape_company_data(ticker: str) -> dict:
    """
    Coleta dados de uma única empresa no Fundamentus.
    """
    url = f"{BASE_URL}detalhes.php?papel={ticker}"
    company_data = {"Ticker": ticker}

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status() # Lança exceção para status HTTP de erro
    except requests.exceptions.RequestException as e:
        logging.warning(f"  Erro ao acessar a página de {ticker}: {e}")
        return company_data

    soup = BeautifulSoup(response.text, "html.parser")

    label_tds = soup.find_all("td", class_="label")
    
    for label_tag in label_tds:
        raw_label_from_html = label_tag.text.strip()
        
        # Remove o ':' e então normaliza para comparação e uso como chave
        processed_label_no_colon = raw_label_from_html.replace(":", "")
        normalized_label = normalize_string_for_comparison(processed_label_no_colon)

        # Este bloco é para SPECIAL_METRICS (Receita Líquida, EBIT, etc.)
        if normalized_label in SPECIAL_METRICS:
            parent_row = label_tag.find_parent("tr")
            if parent_row:
                data_cells = parent_row.find_all("td", class_="data")
                if len(data_cells) >= 2:
                    value_12m = data_cells[0].text.strip()
                    value_3m = data_cells[1].text.strip()

                    # Adiciona ao dicionário com os nomes normalizados e sufixos
                    company_data[f"{normalized_label} 12m"] = value_12m
                    company_data[f"{normalized_label} 3m"] = value_3m
        else:
            data_tag = label_tag.find_next_sibling("td", class_="data")
            if data_tag:
                value = data_tag.text.strip()
                company_data[normalized_label] = value # Usa o nome normalizado como chave
    
    # Após popular company_data, processa os valores
    for key, value in company_data.items():
        # Verifica se a chave (label normalizado) está em STRING_FIELDS
        # E também não converte colunas que serão tratadas como datas
        if key != "Ticker" and key not in STRING_FIELDS and clean_column_name(key) not in DATE_COLUMNS_TO_CONVERT:
            company_data[key] = clean_and_convert_value(value)

    time.sleep(random.uniform(0.1, 0.5)) # Pequeno delay para evitar sobrecarga no servidor
    return company_data

def get_all_tickers() -> list:
    """
    Obtém a lista de todos os tickers de empresas disponíveis no Fundamentus.
    """
    logging.info("Obtendo lista de todos os tickers do Fundamentus...")
    tickers = []
    try:
        response = requests.get(f"{BASE_URL}resultado.php", headers=HEADERS, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        table = soup.find("table", class_="resultado")
        
        if table:
            rows = table.find_all("tr")
            for row in rows[1:]: # Ignora a linha de cabeçalho
                cols = row.find_all("td")
                if cols and cols[0].find('a'): # Verifica se a primeira coluna contém um link (um ticker)
                    ticker = cols[0].text.strip()
                    tickers.append(ticker)
        else:
            logging.warning("    AVISO: Tabela de resultados não encontrada na página de tickers.")
    except requests.exceptions.RequestException as e:
        logging.error(f"  Erro ao acessar a página de resultados para obter tickers: {e}")
    
    logging.info(f"  {len(tickers)} tickers encontrados.")
    return tickers

# --- Função principal para ETL (versão local) ---
def etl_fundamentus_data():
    """
    Função principal que orquestra o processo de ETL (Extração, Transformação)
    dos dados fundamentalistas do Fundamentus para execução local.
    """
    start_time = time.time()

    # --- Obter o timestamp de execução local ---
    timestamp_local = datetime.now()
    logging.info(f"Execução local, usando data/hora atual: {timestamp_local.isoformat()}")

    # --- Extração ---
    all_tickers = get_all_tickers() 
    if not all_tickers:
        logging.error("Nenhum ticker encontrado. Encerrando o processo ETL.")
        return pd.DataFrame() 

    all_companies_data = []
    MAX_WORKERS = 8 
    
    logging.info(f"\nIniciando coleta de dados para {len(all_tickers)} empresas usando {MAX_WORKERS} threads...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(scrape_company_data, ticker): ticker for ticker in all_tickers}
        
        processed_count = 0
        for future in concurrent.futures.as_completed(futures):
            ticker = futures[future]
            try:
                data = future.result()
                if data:
                    # Adiciona o timestamp de execução a cada registro
                    data['Data_Execucao'] = timestamp_local
                    all_companies_data.append(data)
            except Exception as exc:
                logging.error(f"  Ticker {ticker} gerou uma exceção durante scraping: {exc}")
            processed_count += 1
            if processed_count % 50 == 0 or processed_count == len(all_tickers):
                logging.info(f"Progresso de scraping: {processed_count}/{len(all_tickers)} empresas processadas.")

    logging.info("\nColeta de dados concluída. Criando DataFrame...")
    df = pd.DataFrame(all_companies_data)
    
    # --- Transformação ---

    # 1) Alterar os nomes das colunas
    original_columns = df.columns.tolist()
    df.columns = [clean_column_name(col) for col in df.columns]
    logging.info(f"Nomes das colunas alterados. Exemplo original: {original_columns[:3]} -> Limpos: {df.columns.tolist()[:3]}")

    # --- Conversão de colunas de data para formato 'YYYY-MM-DD' ---
    for col_name in DATE_COLUMNS_TO_CONVERT:
        if col_name in df.columns:
            # Explicitamente substitui '-' (e outros valores que podem indicar nulo) por pd.NA
            df[col_name] = df[col_name].replace(['-', ''], pd.NA)
            
            # Converte para objetos datetime. Datas inválidas se tornam NaT (Not a Time).
            df[col_name] = pd.to_datetime(df[col_name], format='%d/%m/%Y', errors='coerce')
            
            # Formata para 'YYYY-MM-DD'. Valores NaT são convertidos para None.
            df[col_name] = df[col_name].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else None)
            logging.info(f"  Coluna '{col_name}' convertida para formato 'YYYY-MM-DD' ou None.")
        else:
            logging.warning(f"  Coluna de data '{col_name}' não encontrada no DataFrame para conversão.")

    # Remover colunas específicas, agora usando os nomes limpos
    if 'papel' in df.columns:
        df.drop(columns=['papel'], inplace=True)
        logging.info("  Coluna 'papel' removida.")
    
    original_cols_count = df.shape[1]
    df.dropna(axis=1, how='all', inplace=True) # Remove colunas totalmente vazias
    if df.shape[1] < original_cols_count:
        logging.info(f"  {original_cols_count - df.shape[1]} colunas totalmente vazias removidas.\n")

    # Colunas numéricas que não são afetadas pela limpeza de nome, mas podem ser removidas se necessário
    cols_to_drop_by_name = ['1', '2', '3', '4'] 
    existing_cols_to_drop = [col for col in cols_to_drop_by_name if col in df.columns]
    if existing_cols_to_drop:
        df.drop(columns=existing_cols_to_drop, inplace=True)
        logging.info(f"  Colunas {existing_cols_to_drop} removidas.\n")

    # 2) Dividir 'data_execucao' em 'data_execucao' (apenas data) e 'hora_execucao'
    if 'data_execucao' in df.columns:
        df['data_execucao'] = pd.to_datetime(df['data_execucao']) # Garante que é datetime para manipulação
        df['hora_execucao'] = df['data_execucao'].dt.strftime('%H:%M:%S') # Extrai apenas a hora
        df['data_execucao'] = df['data_execucao'].dt.strftime('%Y-%m-%d') # Formata 'data_execucao' como 'YYYY-MM-DD'
        logging.info("  Coluna 'data_execucao' dividida em 'data_execucao' (somente data) e 'hora_execucao'.\n")
    else:
        logging.warning("  Coluna 'data_execucao' não encontrada para divisão de data/hora.\n")

    # Reordenar colunas com os novos nomes limpos e a nova coluna 'hora_execucao'
    current_columns = df.columns.tolist()
    year_columns = []
    other_columns = []
    
    for col in current_columns:
        # Regex para anos: Apenas 4 dígitos numéricos (como '2020')
        if re.fullmatch(r'\d{4}', col) and 1900 <= int(col) <= 2100: 
            year_columns.append(col)
        else:
            other_columns.append(col)
            
    year_columns.sort(key=int) 
    
    final_column_order = []
    # Posicionar 'ticker', 'data_execucao' e 'hora_execucao' no início
    if 'ticker' in other_columns:
        final_column_order.append('ticker')
        other_columns.remove('ticker')
    
    if 'data_execucao' in other_columns:
        final_column_order.append('data_execucao')
        other_columns.remove('data_execucao')

    if 'hora_execucao' in other_columns:
        final_column_order.append('hora_execucao')
        other_columns.remove('hora_execucao')
    
    final_column_order.extend(other_columns) 
    final_column_order.extend(year_columns)  
    
    df = df[final_column_order] 
    
    logging.info("\nDataFrame final após transformações. Primeiras 5 linhas:")
    logging.info(f"\n{df.head().to_string()}") 
    
    logging.info("\nInformações do DataFrame final:")
    df.info()

    # --- Salvar CSV com nome dinâmico ---
    try:
        # Garante que a pasta 'data' exista
        import os
        os.makedirs('data', exist_ok=True)

        csv_filename = f"carga_fundamentus_{timestamp_local.strftime('%Y%m%d_%H%M%S')}.csv"
        csv_filepath = f"data/{csv_filename}" 
        df.to_csv(csv_filepath, index=False, encoding="utf-8-sig")
        logging.info(f"\nDados salvos em '{csv_filepath}'")
    except Exception as e:
        logging.error(f"Erro ao salvar o arquivo CSV: {e}")

    end_time = time.time() 
    total_time = end_time - start_time 
    logging.info(f"\nProcesso ETL finalizado em {total_time:.2f} segundos. ✅") 

    return df 

# --- Bloco de execução principal para testes locais ---
if __name__ == "__main__":
    logging.warning("Executando o script localmente para extração e limpeza de dados.")
    logging.warning("A parte de carga para o SQL Server foi desativada para esta execução local.")

    # Chama a função principal de ETL
    final_df = etl_fundamentus_data()

    if final_df is not None and not final_df.empty:
        logging.info("\n--- Dados Extraídos e Limpos (Primeiras 10 linhas) ---")
        print(final_df.head(10).to_string())
        logging.info(f"\nDataFrame final contém {len(final_df)} linhas e {len(final_df.columns)} colunas.")
    else:
        logging.warning("Nenhum dado foi processado ou o DataFrame está vazio.")
