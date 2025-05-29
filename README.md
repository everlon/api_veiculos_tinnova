# Sistema de Registro de Veículos

Este projeto implementa um sistema back-end para o registro e gerenciamento de veículos, conforme os requisitos especificados. A aplicação fornece uma API RESTful completa com funcionalidades de CRUD, filtros, estatísticas e listagem de veículos recentes e não vendidos.

## Requisitos do Sistema

Para configurar e executar este projeto, você precisará ter instalado:

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/)

## Configuração e Execução

Siga os passos abaixo para colocar o projeto em funcionamento:

1.  Clone o repositório:

    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd tinnova
    ```

2.  Configurar variáveis de ambiente:

    O projeto utiliza variáveis de ambiente para a configuração do banco de dados. Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo (certifique-se de substituir os valores conforme necessário):

    ```dotenv
    # Configurações do Banco de Dados MySQL
    DB_HOST=db
    DB_PORT=3306
    DB_NAME=tinnova_db
    DB_USER=USERNAME
    DB_PASSWORD=PASSWORD
    ```

3.  Construir e iniciar os contêineres Docker:

    ```bash
    docker-compose up --build -d
    ```

    Este comando irá construir as imagens Docker e iniciar os serviços (API e banco de dados) em segundo plano.

4.  Executar as migrações do banco de dados (Alembic):

    É necessário aplicar as migrações para criar as tabelas no banco de dados. Execute o comando abaixo após os contêineres estarem rodando:

    ```bash
    docker-compose exec api alembic upgrade head
    ```

## Executando os Testes

Para executar os testes automatizados do projeto, utilize o seguinte comando:

```bash
docker-compose exec tinnova_api pytest tests/test_veiculo.py -v
```

Este comando espera o banco de dados estar pronto, executa as migrações do Alembic e então roda os testes pytest no contêiner da API.

## Documentação da API (Swagger/OpenAPI)

Com a aplicação em execução (passo 3), você pode acessar a documentação interativa da API nos seguintes endereços:

*   **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

Esta documentação é gerada automaticamente pelo FastAPI e permite explorar e testar os endpoints da API.

## Endpoints da API

A API de veículos segue o padrão RESTful e disponibiliza os seguintes endpoints:

*   `GET /veiculos`: Lista todos os veículos, com suporte a filtros por `marca`, `ano` e `cor`/`descricao`, além de paginação (`skip`, `limit`).
*   `GET /veiculos/{id}`: Retorna os detalhes de um veículo específico pelo seu ID.
*   `POST /veiculos`: Cria um novo veículo. Requer um corpo de requisição com os dados do veículo (`veiculo`, `marca`, `ano`, `descricao`, `vendido`). Inclui validação para ano e marca.
*   `PUT /veiculos/{id}`: Atualiza completamente os dados de um veículo existente pelo seu ID. Requer um corpo de requisição com os dados completos do veículo. Inclui validação para ano e marca.
*   `PATCH /veiculos/{id}`: Atualiza parcialmente os dados de um veículo existente pelo seu ID. Requer um corpo de requisição com os campos a serem atualizados.
*   `DELETE /veiculos/{id}`: Remove um veículo existente pelo seu ID.
*   `GET /veiculos/estatisticas/geral`: Retorna estatísticas consolidadas sobre os veículos (total não vendidos, distribuição por década e fabricante, veículos recentes).
*   `GET /veiculos/nao-vendidos/`: Lista todos os veículos que estão marcados como não vendidos.
*   `GET /veiculos/recentes/`: Lista os veículos que foram cadastrados nos últimos 7 dias.

## Critérios de Avaliação (Considerações)

Este projeto foi desenvolvido com foco nos seguintes critérios:

*   **Facilidade de configuração:** Utiliza Docker e Docker Compose para criar um ambiente consistente e fácil de configurar.
*   **Performance:** A arquitetura com FastAPI e SQLAlchemy em Python é conhecida por sua boa performance para APIs web.
*   **Código limpo e Boas práticas:** O código é organizado em camadas (routes, services, crud, models, schemas), utiliza tipagem estática e segue convenções de nomenclatura. Boas práticas como injeção de dependência e tratamento de exceções são aplicadas.
*   **Documentação de código e projeto:** As docstrings nas funções e a documentação no README visam clarear o funcionamento do código e do projeto como um todo. A documentação Swagger/OpenAPI é gerada automaticamente.
*   **Testes Unitários:** O projeto inclui testes automatizados abrangentes para a maioria dos endpoints da API, garantindo a funcionalidade e prevenindo regressões.
*   **Design Patterns:** A estrutura do projeto reflete padrões comuns em desenvolvimento de APIs, como a separação em camadas (Service Layer, Data Access Layer - CRUD) e o uso de Data Transfer Objects (DTOs) via Pydantic Schemas.

Este README fornece uma visão geral do projeto. Para detalhes mais aprofundados sobre os endpoints e schemas, consulte a documentação interativa do Swagger/OpenAPI.
