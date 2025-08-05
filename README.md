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
```
O script criará uma pasta data/ no mesmo diretório e salvará o arquivo CSV lá.


## 👨‍💻 Estrutura do Código
O código é dividido em funções lógicas para facilitar a compreensão:

* normalize_string_for_comparison(s: str) -> str: Função utilitária para limpar e padronizar strings, removendo acentos, caracteres especiais e espaços extras.
* clean_and_convert_value(value_str): Converte strings de valores monetários ou percentuais para números de ponto flutuante.
* clean_column_name(col_name: str) -> str: Normaliza os nomes das colunas do DataFrame, removendo caracteres especiais e formatando para snake_case.
* scrape_company_data(ticker: str) -> dict: Realiza o scraping dos dados de uma única empresa dado seu ticker.
* get_all_tickers() -> list: Extrai a lista de todos os tickers disponíveis no Fundamentus.
* etl_fundamentus_data(): A função principal que orquestra todo o processo de Extração (E), Transformação (T) e salvamento dos dados para uso local.

## 📄 Exemplo de Saída (CSV)
Após a execução, um arquivo CSV será gerado na pasta data/ com uma estrutura similar a esta:

ticker,data_execucao,hora_execucao,tipo,empresa,setor,subsetor,data_ult_cot,ult_balanco_processado,cotacao,pl,pvp,psr,dy,pa_ativo,pcg,pebit,pacl,evebit,evebitda,mrgebit,mrgliq,liqcorrente,roic,roe,liqc2meses,pativo,divbruta_patrim,cres_receita_5a,receita_liquida_12m,receita_liquida_3m,ebit_12m,ebit_3m,lucro_liquido_12m,lucro_liquido_3m,result_int_financ_12m,result_int_financ_3m,rec_servicos_12m,rec_servicos_3m,ult_12_meses_receita_liquida,ult_12_meses_ebit,ult_12_meses_lucro_liquido,ult_3_meses_receita_liquida,ult_3_meses_ebit,ult_3_meses_lucro_liquido,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014,2013,2012
PETR4,2024-04-28,10:30:00,ON,PETROBRAS PN,Petroleo Gas e Biocombustiveis,Petroleo Gas e Biocombustiveis,2024-04-26,2023-12-31,40.97,4.86,1.44,0.72,9.15,0.79,0.59,2.83,0.55,1.75,1.52,25.46,14.77,1.17,22.25,31.78,20.0,0.92,0.67,11.53,564032.0,154789.0,143615.0,37835.0,83284.0,22378.0,1121.0,432.0,0.0,0.0,564032.0,143615.0,83284.0,154789.0,37835.0,22378.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
VALE3,2024-04-28,10:30:00,ON,VALE ON NM,Mineração,Minerais Metálicos,2024-04-26,2023-12-31,64.24,6.48,1.4,1.86,9.39,0.73,0.56,3.01,0.53,1.67,1.38,28.67,19.34,1.21,20.3,21.65,15.0,0.89,0.71,8.91,223000.0,55750.0,63950.0,16000.0,42000.0,10500.0,500.0,120.0,0.0,0.0,223000.0,63950.0,42000.0,55750.0,16000.0,10500.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0


## 🤝 Contribuindo
Este é um projeto desenvolvido para fins de estudo e portfólio. No momento, não estou buscando contribuições externas. No entanto, sinta-se à vontade para fazer um fork, explorar e adaptar o código para suas necessidades!


## 📧 Contato

Felipe Avila

[github.com](https://github.com/f-avila-84)

[linkedin.com](https://linkedin.com/in/avilafelipe)

## 📜 Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
opensource.org


Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
