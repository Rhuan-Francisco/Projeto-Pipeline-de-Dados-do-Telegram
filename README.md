# 📊 Projeto: Pipeline de Dados do Telegram

<img width="601" height="321" alt="projeto" src="https://github.com/user-attachments/assets/418e39fd-0b2a-49ea-8aea-9a688aab2297" />

Este projeto demonstra a construção de um pipeline de dados básico para ingestão, processamento (ETL) e apresentação de mensagens do Telegram, utilizando serviços da AWS.

## 📌 Contexto

Este projeto aborda a criação de um pipeline de dados focado em mensagens de texto do Telegram. A arquitetura proposta visa capturar dados transacionais (mensagens) de um bot do Telegram, transformá-los em dados analíticos e disponibilizá-los para consultas. 

## 🚀 1. Ingestão

A etapa de **ingestão** é responsável por coletar os dados brutos, no seu formato original (JSON), diretamente da fonte. Para este projeto, as mensagens do Telegram são capturadas e persistidas na AWS da seguinte forma:

*   **Fonte de Dados**: Um bot do Telegram, configurado para interagir com um grupo específico.
*   **Mecanismo de Coleta**: Utiliza um *webhook* do Telegram, que redireciona as mensagens em tempo real para uma API web externa.
*   **AWS API Gateway**: Atua como o endpoint HTTP que recebe as mensagens do *webhook* do Telegram.
*   **AWS Lambda (Função de Ingestão)**: Acionada pelo API Gateway, esta função verifica se a mensagem provém do grupo correto do Telegram e a persiste, sem transformações, em um bucket S3. As mensagens são armazenadas em formato JSON, preservando sua estrutura original.
*   **AWS S3 (Camada Raw)**: Um bucket S3 (`rhuan-projetoebac-datalake-raw`) serve como o *data lake* para armazenar os dados brutos ingeridos. A escolha do armazenamento em formato original permite flexibilidade para reprocessamentos futuros.

## 🔄 2. ETL

A etapa de **Extração, Transformação e Carregamento (ETL)** processa os dados brutos para torná-los mais adequados para análise. As mensagens de um dia inteiro, armazenadas na camada raw, são limpas, transformadas e agregadas em um formato otimizado para consultas analíticas:

*   **AWS Lambda (Função de ETL)**: Acionada diariamente, esta função realiza os seguintes passos:
    *   Lista todos os arquivos JSON (mensagens) do dia anterior na camada raw do S3.
    *   Baixa cada arquivo, carrega seu conteúdo e aplica uma função de *data wrangling* para extrair e normalizar campos relevantes (message_id, user_id, chat_id, text, date, etc.).
    *   Concatena os dados processados em uma tabela PyArrow.
    *   Persiste a tabela resultante em formato Parquet na camada enriquecida do S3. Este formato é colunar e comprimido, otimizando o armazenamento e a performance de leitura.
    *   🔖 O arquivo com o codigo Python utilizado no Lambda é `lambda raw.py`.
    
*   **AWS S3 (Camada Enriquecida)**: Um segundo bucket S3 (`projetoebac-datalake-enriched`) armazena os dados após o processamento ETL. Este bucket contém dados organizados por data, prontos para análise.
    *   🔖 O arquivo com o codigo Python utilizado no Lambda é `lambda enriched.py`.
    
*   **AWS Event Bridge**: Configurado para atuar como um *scheduler*, ele aciona a função AWS Lambda de ETL diariamente, garantindo que os dados do dia anterior sejam processados de forma recorrente.

## 📈 3. Apresentação

A etapa de **apresentação** disponibiliza os dados processados para os usuários finais e outras ferramentas analíticas, utilizando uma interface amigável como SQL:

*   **AWS Athena**: Um serviço de consulta interativa que permite executar queries SQL diretamente sobre os dados armazenados na camada enriquecida do S3, sem a necessidade de provisionar servidores.
*   **Tabela Externa SQL**: É criada uma tabela externa no Athena que mapeia a estrutura dos arquivos Parquet no S3. Isso permite que os usuários consultem os dados usando SQL como se estivessem interagindo com um banco de dados tradicional.
*  📁  As consultas utilizadas e suas respostas estão no Notebook `Querys no AWS Athena.ipynb`

## 🧠 Tecnologias Utilizadas

- Python 
- AWS Lambda 
- AWS S3 
- AWS API Gateway 
- AWS EventBridge 
- AWS Athena 
- PyArrow 
- Telegram Bot API ]

## 📄 Licença

Este projeto utiliza a licença MIT.
