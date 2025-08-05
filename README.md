# 📈 Scraper de Dados Fundamentalistas do site Fundamentus

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Libraries](https://img.shields.io/badge/Libraries-requests%2C%20beautifulsoup4%2C%20pandas-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📊 Visão Geral do Projeto

Este repositório contém um script em Python projetado para coletar (scraper) dados fundamentalistas de empresas listadas na bolsa brasileira, utilizando como fonte o site [Fundamentus](http://www.fundamentus.com.br/). O objetivo é fornecer uma ferramenta eficiente para extrair informações financeiras e indicadores de mercado de forma automatizada, processá-las e salvá-las em um formato estruturado (CSV) para análises posteriores.

Se você é um investidor, analista de dados ou simplesmente busca dados organizados para estudar o mercado financeiro brasileiro, este script pode ser um excelente ponto de partida!

## ✨ Funcionalidades Principais

*   **Coleta Abrangente:** Extrai uma vasta gama de dados fundamentalistas para todas as ações disponíveis no Fundamentus, incluindo indicadores como P/L, VPA, Margens, Receita Líquida, EBIT e muito mais.
*   **Paralelismo Eficiente:** Utiliza `concurrent.futures.ThreadPoolExecutor` para realizar a coleta de dados de múltiplas empresas simultaneamente, otimizando o tempo de execução.
*   **Limpeza e Normalização de Dados:** Realiza a sanitização de nomes de colunas e a conversão de valores (moedas, porcentagens, datas) para formatos numéricos e padronizados, facilitando a análise.
*   **Exportação em CSV:** Os dados coletados e transformados são salvos automaticamente em um arquivo CSV, com um nome dinâmico que inclui a data e hora da execução, garantindo a organização das coletas.
*   **Logging Detalhado:** Implementação de logs que informam o progresso da coleta, avisos e erros, proporcionando transparência e auxiliando na depuração.
*   **Estrutura Modular:** O código é organizado em funções bem definidas, facilitando a compreensão, manutenção e possíveis extensões.

## 🤖 Como Funciona (para não programadores)

Este script atua como um "robô" na internet, seguindo estes passos simples:

1.  **Visita o Site:** Primeiro, ele vai até o site do Fundamentus, que é uma grande fonte de informações sobre empresas.
2.  **Encontra as Empresas:** Lá, ele pega a lista de todas as empresas (ações) que ele pode pesquisar.
3.  **Visita Cada Empresa:** Para cada empresa da lista, o robô visita a página específica dela, como se você estivesse clicando em cada ação no site.
4.  **Copia os Dados:** De cada página, ele "copia" todas as informações importantes, como o preço da ação, o lucro da empresa, o setor, etc.
5.  **Organiza e Limpa:** Depois de copiar tudo, ele organiza esses dados de uma forma fácil de entender, limpando caracteres estranhos e garantindo que números e datas estejam no formato certo.
6.  **Salva em um Arquivo:** Por fim, ele salva tudo em um arquivo do tipo `CSV` (como uma planilha), dentro de uma pasta chamada `data`. O nome do arquivo terá a data e hora que você o executou, como `carga_fundamentus_20240428_103000.csv`.

Pronto! Com esse arquivo CSV, você pode abrir no Excel, Google Sheets ou qualquer ferramenta de análise de dados para visualizar e trabalhar com as informações das empresas.

## ⚙️ Configuração e Uso (para programadores)

### Pré-requisitos

Certifique-se de ter o [Python](https://www.python.org/downloads/) instalado em sua máquina (versão 3.x recomendada).

### Instalação

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/f-avila-84/Fundamentus_ETL_local.git
    cd NomeDoSeuRepositorio
    ```
    
2.  **Crie e Ative um Ambiente Virtual (Opcional, mas recomendado):**
    ```bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install requests beautifulsoup4 pandas lxml
    ```
    (`lxml` é uma dependência recomendada para `beautifulsoup4` para melhor performance.)

### Como Executar

Para executar o script, basta rodar o arquivo Python a partir do seu terminal:

```bash
python seu_script_aqui.py

O script criará uma pasta data/ no mesmo diretório e salvará o arquivo CSV lá.


## 👨‍💻 Estrutura do Código
O código é dividido em funções lógicas para facilitar a compreensão:

normalize_string_for_comparison(s: str) -> str: Função utilitária para limpar e padronizar strings, removendo acentos, caracteres especiais e espaços extras.
clean_and_convert_value(value_str): Converte strings de valores monetários ou percentuais para números de ponto flutuante.
clean_column_name(col_name: str) -> str: Normaliza os nomes das colunas do DataFrame, removendo caracteres especiais e formatando para snake_case.
scrape_company_data(ticker: str) -> dict: Realiza o scraping dos dados de uma única empresa dado seu ticker.
get_all_tickers() -> list: Extrai a lista de todos os tickers disponíveis no Fundamentus.
etl_fundamentus_data(): A função principal que orquestra todo o processo de Extração (E), Transformação (T) e salvamento dos dados para uso local.

