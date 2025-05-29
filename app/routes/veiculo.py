from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.veiculo import VeiculoService
from app.schemas.veiculo import (
    VeiculoCreate,
    VeiculoUpdate,
    Veiculo
)

router = APIRouter(
    prefix="/veiculos",
    tags=["veiculos"],
    responses={404: {"description": "Veículo não encontrado"}},
)

def get_veiculo_service(db: Session = Depends(get_db)) -> VeiculoService:
    """
    Dependency injection para o serviço de veículos.
    """
    return VeiculoService(db)

@router.post("/", response_model=Veiculo, status_code=201,
    summary="Cria um novo veículo",
    response_description="O veículo recém-criado"
)
def criar_veiculo(
    veiculo: VeiculoCreate,
    service: VeiculoService = Depends(get_veiculo_service)
):
    """
    **Criação de Novo Veículo**

    Este endpoint permite cadastrar um novo veículo no sistema. É necessário fornecer todos os dados do veículo no corpo da requisição.

    **Regras de Negócio:**
    - O ano do veículo deve ser válido (entre 1900 e o ano atual + 1).
    - A marca do veículo deve estar na lista de marcas permitidas.

    **Casos de Uso:**
    - Registrar um veículo recém-adquirido ou fabricado.

    **Respostas:**
    - `201 Created`: Retorna o objeto do veículo criado com seus dados completos.
    - `400 Bad Request`: Se o ano ou a marca forem inválidos.
    - `422 Unprocessable Entity`: Se o corpo da requisição não seguir o schema esperado.
    """
    return service.criar_veiculo(veiculo)

@router.get("/{veiculo_id}", response_model=Veiculo,
    summary="Obtém os detalhes de um veículo",
    response_description="Detalhes do veículo solicitado"
)
def obter_veiculo(
    veiculo_id: int,
    service: VeiculoService = Depends(get_veiculo_service)
):
    """
    **Obtenção de Detalhes do Veículo**

    Este endpoint retorna as informações detalhadas de um veículo específico com base no seu ID.

    **Casos de Uso:**
    - Visualizar todos os dados de um veículo individualmente.

    **Respostas:**
    - `200 OK`: Retorna o objeto do veículo com seus dados completos.
    - `404 Not Found`: Se nenhum veículo com o ID fornecido for encontrado.
    """
    return service.obter_veiculo(veiculo_id)

@router.get("/", response_model=List[Veiculo],
    summary="Lista todos os veículos com filtros opcionais",
    response_description="Lista de veículos"
)
def listar_veiculos(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=100, description="Limite de registros por página"),
    marca: Optional[str] = Query(None, description="Filtrar por marca (busca parcial e case-insensitive)"),
    ano: Optional[int] = Query(None, ge=1900, description="Filtrar por ano exato"),
    cor: Optional[str] = Query(None, description="Filtrar por descrição/cor (busca parcial e case-insensitive)"),
    service: VeiculoService = Depends(get_veiculo_service)
):
    """
    **Listagem de Veículos**

    Este endpoint retorna uma lista de veículos, permitindo aplicar filtros e controlar a paginação.

    **Filtros:**
    - `marca`: Filtra veículos cuja marca contenha o texto especificado (case-insensitive).
    - `ano`: Filtra veículos por ano exato.
    - `cor`: Filtra veículos cuja descrição/cor contenha o texto especificado (case-insensitive).

    **Paginação:**
    - `skip`: Número de veículos para pular (para offset).
    - `limit`: Número máximo de veículos a retornar.

    **Casos de Uso:**
    - Exibir a lista completa de veículos.
    - Buscar veículos por critérios específicos (marca, ano, cor).
    - Implementar paginação em interfaces de usuário.

    **Respostas:**
    - `200 OK`: Retorna uma lista de objetos de veículo.
    """
    return service.listar_veiculos(
        skip=skip,
        limit=limit,
        marca=marca,
        ano=ano,
        cor=cor
    )

@router.put("/{veiculo_id}", response_model=Veiculo,
    summary="Atualiza completamente um veículo existente",
    response_description="O veículo atualizado"
)
def atualizar_veiculo(
    veiculo_id: int,
    veiculo_update: VeiculoUpdate,
    service: VeiculoService = Depends(get_veiculo_service)
):
    """
    **Atualização Completa de Veículo (PUT)**

    Este endpoint permite substituir completamente os dados de um veículo existente identificado pelo seu ID.

    **Regras de Negócio:**
    - Todas as validações de criação se aplicam aos dados fornecidos (ano e marca).

    **Casos de Uso:**
    - Corrigir ou atualizar todas as informações de um veículo.

    **Respostas:**
    - `200 OK`: Retorna o objeto do veículo atualizado.
    - `400 Bad Request`: Se o ano ou a marca fornecidos forem inválidos.
    - `404 Not Found`: Se nenhum veículo com o ID especificado for encontrado.
    - `422 Unprocessable Entity`: Se o corpo da requisição não seguir o schema esperado.
    """
    return service.atualizar_veiculo(veiculo_id, veiculo_update)

@router.delete("/{veiculo_id}",
    summary="Remove um veículo",
    response_description="Mensagem de sucesso após remoção"
)
def remover_veiculo(
    veiculo_id: int,
    service: VeiculoService = Depends(get_veiculo_service)
):
    """
    **Remoção de Veículo**

    Este endpoint permite excluir um veículo da base de dados utilizando seu ID.

    **Casos de Uso:**
    - Remover um veículo que não faz mais parte do inventário.

    **Respostas:**
    - `200 OK`: Retorna uma mensagem de sucesso indicando que o veículo foi removido.
    - `404 Not Found`: Se nenhum veículo com o ID fornecido for encontrado.
    """
    return service.remover_veiculo(veiculo_id)

@router.get("/estatisticas/geral",
    summary="Retorna estatísticas gerais sobre os veículos",
    response_description="Objeto com estatísticas"
)
def obter_estatisticas(
    service: VeiculoService = Depends(get_veiculo_service)
):
    """
    **Estatísticas Gerais de Veículos**

    Este endpoint fornece diversas estatísticas consolidadas sobre o inventário de veículos.

    **Regras de Negócio/Informações Calculadas:**
    - **Total de veículos não vendidos:** Conta todos os veículos onde `vendido` é `False`.
    - **Distribuição por década:** Agrupa e conta veículos pela década de fabricação (ex: 1990s, 2000s).
    - **Distribuição por fabricante:** Agrupa e conta veículos por marca/fabricante.
    - **Veículos recentes:** Conta veículos criados nos últimos 7 dias.

    **Casos de Uso:**
    - Obter um panorama geral do inventário de veículos.
    - Análise rápida sobre o estado das vendas e o perfil da base de veículos.

    **Respostas:**
    - `200 OK`: Retorna um objeto JSON contendo as estatísticas.
    """
    return service.obter_estatisticas()

@router.get("/nao-vendidos/", response_model=List[Veiculo],
    summary="Lista todos os veículos não vendidos",
    response_description="Lista de veículos não vendidos"
)
def listar_veiculos_nao_vendidos(
    service: VeiculoService = Depends(get_veiculo_service)
):
    """
    **Listagem de Veículos Não Vendidos**

    Este endpoint retorna uma lista apenas dos veículos cujo status `vendido` é `False`.

    **Casos de Uso:**
    - Identificar rapidamente o estoque de veículos ainda disponíveis para venda.

    **Respostas:**
    - `200 OK`: Retorna uma lista de objetos de veículo não vendidos.
    """
    return service.obter_veiculos_nao_vendidos()

@router.get("/recentes/", response_model=List[Veiculo],
    summary="Lista veículos cadastrados nos últimos 7 dias",
    response_description="Lista de veículos recentes"
)
def listar_veiculos_recentes(
    service: VeiculoService = Depends(get_veiculo_service)
):
    """
    **Listagem de Veículos Recentes**

    Este endpoint retorna uma lista dos veículos que foram cadastrados no sistema nos últimos 7 dias.

    **Casos de Uso:**
    - Visualizar os veículos adicionados recentemente ao inventário.

    **Respostas:**
    - `200 OK`: Retorna uma lista de objetos de veículo recentes.
    """
    return service.obter_veiculos_recentes()
