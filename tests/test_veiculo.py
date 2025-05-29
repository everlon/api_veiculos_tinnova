import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from sqlalchemy.sql import text

from unittest.mock import Mock, patch

from app.main import app
from app.database import Base, get_db
from app.models.veiculo import Veiculo as VeiculoModel
from app.schemas.veiculo import VeiculoCreate, VeiculoUpdate
from app.services.veiculo import VeiculoService
from app.src.veiculo import (
    get_veiculo as crud_get_veiculo,
    update_veiculo as crud_update_veiculo,
    create_veiculo as crud_create_veiculo,
    validar_marca as crud_validar_marca
)

API_PREFIX = "/api/v1"

SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
        db.rollback()
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def setup_test_db():
    with engine.connect() as connection:
        connection.execute(text("SET SESSION sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''))"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture(scope="function")
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client():
    # Garante que as tabelas já foram criadas antes de inicializar
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def veiculo_data():
    return {
        "veiculo": "Gol",
        "marca": "Volkswagen",
        "ano": 2020,
        "descricao": "Gol 1.0",
        "vendido": False
    }

@pytest.fixture(scope="function")
def veiculo_criado(setup_test_db, client, veiculo_data):
    response = client.post(f"{API_PREFIX}/veiculos/", json=veiculo_data)
    assert response.status_code == 201
    return response.json()

# Testes CRUD
def test_criar_veiculo(setup_test_db, client, veiculo_data):
    response = client.post(f"{API_PREFIX}/veiculos/", json=veiculo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["veiculo"] == veiculo_data["veiculo"]
    assert data["marca"] == veiculo_data["marca"]
    assert data["ano"] == veiculo_data["ano"]
    assert "id" in data
    assert "created" in data
    assert "updated" in data

def test_obter_veiculo(setup_test_db, client, veiculo_criado):
    response = client.get(f"{API_PREFIX}/veiculos/{veiculo_criado['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == veiculo_criado["id"]
    assert data["veiculo"] == veiculo_criado["veiculo"]

def test_atualizar_veiculo(setup_test_db, client, veiculo_criado):
    update_data = {
        "veiculo": "Gol G6 Turbo",
        "marca": "Volkswagen",
        "ano": 2021,
        "descricao": "Gol G6 1.6 Turbo com upgrades",
        "vendido": True
    }
    response = client.put(f"{API_PREFIX}/veiculos/{veiculo_criado['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["veiculo"] == update_data["veiculo"]
    assert data["marca"] == update_data["marca"]
    assert data["ano"] == update_data["ano"]
    assert data["descricao"] == update_data["descricao"]
    assert data["vendido"] == update_data["vendido"]
    assert data["id"] == veiculo_criado["id"]

def test_remover_veiculo(setup_test_db, client, veiculo_criado):
    response = client.delete(f"{API_PREFIX}/veiculos/{veiculo_criado['id']}")
    assert response.status_code == 200
    response = client.get(f"{API_PREFIX}/veiculos/{veiculo_criado['id']}")
    assert response.status_code == 404

# Testes de Filtros
def test_listar_veiculos_com_filtros(setup_test_db, client, db):
    db.execute(text("TRUNCATE TABLE veiculos"))
    veiculos_payload = [
        {"veiculo": "Gol", "marca": "Volkswagen", "ano": 2020, "descricao": "Gol 1.0", "vendido": False},
        {"veiculo": "Onix", "marca": "Chevrolet", "ano": 2021, "descricao": "Onix 1.0", "vendido": True},
        {"veiculo": "HB20", "marca": "Hyundai", "ano": 2019, "descricao": "HB20 1.0", "vendido": False}
    ]
    for veiculo in veiculos_payload:
        client.post(f"{API_PREFIX}/veiculos/", json=veiculo)

    # Testar filtro por marca
    response = client.get(f"{API_PREFIX}/veiculos/?marca=Volkswagen")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["marca"] == "Volkswagen"

    # Testar filtro por ano
    response = client.get(f"{API_PREFIX}/veiculos/?ano=2021")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["ano"] == 2021

    response_cor = client.get(f"{API_PREFIX}/veiculos/?cor=Gol")
    assert response_cor.status_code == 200
    data_cor = response_cor.json()
    assert len(data_cor) >= 1
    assert "Gol" in data_cor[0]["veiculo"]

def test_listar_veiculos_nao_vendidos_lista_vazia(setup_test_db, client, db):
    db.execute(text("TRUNCATE TABLE veiculos"))
    client.post(f"{API_PREFIX}/veiculos/", json={
        "veiculo": "Carro Vendido 1", "marca": "Ford", "ano": 2020,
        "descricao": "...", "vendido": True
    })
    client.post(f"{API_PREFIX}/veiculos/", json={
        "veiculo": "Carro Vendido 2", "marca": "Fiat", "ano": 2021,
        "descricao": "...", "vendido": True
    })

    response = client.get(f"{API_PREFIX}/veiculos/nao-vendidos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0 # Espera uma lista vazia

# Testes de Estatísticas
def test_estatisticas_veiculos(setup_test_db, client, db):
    db.execute(text("TRUNCATE TABLE veiculos"))
    veiculos_payload = [
        {"veiculo": "Gol Estatistica", "marca": "Volkswagen", "ano": 2020, "descricao": "Gol para estatistica", "vendido": False},
        {"veiculo": "Onix Estatistica", "marca": "Chevrolet", "ano": 2021, "descricao": "Onix para estatistica", "vendido": True},
        {"veiculo": "HB20 Estatistica", "marca": "Hyundai", "ano": 2019, "descricao": "HB20 para estatistica", "vendido": False}
    ]
    for veiculo in veiculos_payload:
        client.post(f"{API_PREFIX}/veiculos/", json=veiculo)

    response = client.get(f"{API_PREFIX}/veiculos/estatisticas/geral")
    assert response.status_code == 200
    data = response.json()
    assert "total_nao_vendidos" in data
    assert "distribuicao_por_decada" in data
    assert "distribuicao_por_fabricante" in data
    assert data["total_nao_vendidos"] == 2
    assert any(d["decada"] == "2020s" and d["quantidade"] >= 1 for d in data["distribuicao_por_decada"])
    assert any(f["fabricante"] == "Volkswagen" and f["quantidade"] == 1 for f in data["distribuicao_por_fabricante"])

# Testes de Validação
def test_validacao_ano_invalido(setup_test_db, client):
    veiculo_data = {
        "veiculo": "Gol",
        "marca": "Volkswagen",
        "ano": 1800,  # Ano inválido
        "descricao": "Gol 1.0",
        "vendido": False
    }
    response = client.post(f"{API_PREFIX}/veiculos/", json=veiculo_data)
    assert response.status_code == 422
    response_json = response.json()
    assert response_json["detail"] == "Erro de validação"
    assert "errors" in response_json
    found_error = False
    for err in response_json["errors"]:
        if err.get("loc") == ["body", "ano"]:
            assert "greater than" in err.get("msg", "").lower()
            found_error = True
            break
    assert found_error, "Erro de validação para o campo 'ano' (gt=1800) não encontrado ou mensagem inesperada."

def test_validacao_ano_futuro(setup_test_db, client):
    ano_futuro = datetime.now().year + 3
    veiculo_data = {
        "veiculo": "Gol",
        "marca": "Volkswagen",
        "ano": ano_futuro,  # Ano futuro
        "descricao": "Gol 1.0",
        "vendido": False
    }
    response = client.post(f"{API_PREFIX}/veiculos/", json=veiculo_data)
    assert response.status_code == 422
    response_json = response.json()
    assert response_json["detail"] == "Erro de validação"
    assert "errors" in response_json
    found_error = False
    for err in response_json["errors"]:
        if err.get("loc") == ["body", "ano"]: # Localização do erro no Pydantic
            # A mensagem exata pode variar dependendo da restrição no schema Pydantic
            # Ex: "Input should be less than or equal to YYYY"
            assert "less than" in err.get("msg", "").lower()
            found_error = True
            break
    assert found_error, "Erro de validação para o campo 'ano' não encontrado ou mensagem inesperada."

def test_criar_veiculo_ano_abaixo_limite_servico(setup_test_db, client):
    ano_teste = 1899
    veiculo_data = {
        "veiculo": "Carro Antigo",
        "marca": "Ford",
        "ano": ano_teste,
        "descricao": "Veículo muito antigo",
        "vendido": False
    }
    response = client.post(f"{API_PREFIX}/veiculos/", json=veiculo_data)
    assert response.status_code == 400
    response_json = response.json()
    assert "detail" in response_json
    assert "Ano inválido" in response_json["detail"]
    assert f"Deve estar entre 1900 e {datetime.now().year}" in response_json["detail"]

def test_criar_veiculo_ano_acima_limite_servico(setup_test_db, client):
    ano_teste = datetime.now().year + 1
    veiculo_data = {
        "veiculo": "Carro do Futuro Próximo",
        "marca": "Tesla",
        "ano": ano_teste,
        "descricao": "Veículo do próximo ano",
        "vendido": False
    }
    response = client.post(f"{API_PREFIX}/veiculos/", json=veiculo_data)
    assert response.status_code == 400
    response_json = response.json()
    assert "detail" in response_json
    assert "Ano inválido" in response_json["detail"]
    assert f"Deve estar entre 1900 e {datetime.now().year}" in response_json["detail"]

def test_validacao_marca_invalida_criacao(setup_test_db, client):
    veiculo_data = {
        "veiculo": "Carro",
        "marca": "MarcaInvalida",  # Marca inválida
        "ano": 2020,
        "descricao": "Descricao",
        "vendido": False
    }
    response = client.post(f"{API_PREFIX}/veiculos/", json=veiculo_data)
    assert response.status_code == 400
    assert "detail" in response.json()
    response_detail_lower = response.json()["detail"].lower()
    assert f"marca inválida: {veiculo_data['marca'].lower()}" in response_detail_lower
    assert "marcas permitidas:" in response_detail_lower
    assert "chevrolet" in response_detail_lower # Verificar algumas marcas específicas
    assert "ford" in response_detail_lower

def test_validacao_marca_invalida_atualizacao(setup_test_db, client, veiculo_criado):
    marca_invalida = "OutraMarcaInvalida"
    update_data = {
        "veiculo": veiculo_criado["veiculo"], # Manter outros campos
        "marca": marca_invalida,
        "ano": veiculo_criado["ano"],
        "descricao": veiculo_criado["descricao"],
        "vendido": veiculo_criado["vendido"]
    }

    response = client.put(f"{API_PREFIX}/veiculos/{veiculo_criado['id']}", json=update_data)
    assert response.status_code == 400
    assert "detail" in response.json()
    response_detail_lower = response.json()["detail"].lower()
    assert f"marca inválida: {marca_invalida.lower()}" in response_detail_lower
    assert "marcas permitidas:" in response_detail_lower
    assert "volkswagen" in response_detail_lower
    assert "fiat" in response_detail_lower

def test_validacao_ano_invalido_atualizacao(setup_test_db, client, veiculo_criado):
    update_data = {
        "ano": 1888 # Ano inválido
    }
    response = client.put(f"{API_PREFIX}/veiculos/{veiculo_criado['id']}", json=update_data)
    assert response.status_code == 400
    response_json = response.json()
    assert "Ano inválido" in response_json["detail"]
    assert f"Deve estar entre 1900 e {datetime.now().year}" in response_json["detail"]

# Testes de Veículos Recentes
def test_veiculos_recentes(setup_test_db, client):
    veiculo_data_recente = {
        "veiculo": "Gol",
        "marca": "Volkswagen",
        "ano": 2020,
        "descricao": "Gol 1.0",
        "vendido": False
    }
    client.post(f"{API_PREFIX}/veiculos/", json=veiculo_data_recente)

    response = client.get(f"{API_PREFIX}/veiculos/recentes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

# Testes de Veículos Não Vendidos
def test_veiculos_nao_vendidos(setup_test_db, client, db):
    db.execute(text("TRUNCATE TABLE veiculos"))
    veiculos_payload = [
        {"veiculo": "Gol", "marca": "Volkswagen", "ano": 2020, "descricao": "Gol não vendido", "vendido": False},
        {"veiculo": "Onix", "marca": "Chevrolet", "ano": 2021, "descricao": "Onix vendido", "vendido": True}
    ]
    for veiculo_item in veiculos_payload:
        client.post(f"{API_PREFIX}/veiculos/", json=veiculo_item)

    response = client.get(f"{API_PREFIX}/veiculos/nao-vendidos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["vendido"] == False
    assert data[0]["veiculo"] == "Gol"

# Testes para endpoints básicos em main.py
def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Bem-vindo ao sistema Tinnova",
        "api_docs": f"/api/docs",
        "api_redoc": f"/api/redoc",
        "frontend_ui": "/ui" # Este é o prefixo do frontend, não da API
    }

def test_atualizar_veiculo_nao_encontrado(setup_test_db, client, veiculo_data):
    # Tenta atualizar um veículo com ID inexistente
    update_data = {
        "veiculo": "Carro Inexistente",
        "vendido": True
    }
    response = client.put(f"{API_PREFIX}/veiculos/99999", json=update_data) # ID 99999 provavelmente não existe
    assert response.status_code == 404
    assert response.json()["detail"] == "Veículo não encontrado"

def test_remover_veiculo_nao_encontrado(setup_test_db, client):
    response = client.delete(f"{API_PREFIX}/veiculos/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Veículo não encontrado"

def test_crud_update_veiculo_nao_encontrado(setup_test_db, db):
    veiculo_update_data = VeiculoUpdate(
        veiculo="Carro Fantasma",
        vendido=True
    )
    updated_veiculo = crud_update_veiculo(db, veiculo_id=99999, veiculo_update=veiculo_update_data)
    assert updated_veiculo is None


def test_crud_validar_marca_existente(setup_test_db, db):
    veiculo_a_criar = VeiculoCreate(
        veiculo="Carro Teste Marca",
        marca="SuperMarcaExistente",
        ano=2022,
        descricao="Teste de validação de marca",
        vendido=False
    )
    crud_create_veiculo(db, veiculo_a_criar)

    assert crud_validar_marca(db, "SuperMarcaExistente") is True
    assert crud_validar_marca(db, "supermarca") is True
    assert crud_validar_marca(db, "Existente") is True

def test_crud_validar_marca_inexistente(setup_test_db, db):
    assert crud_validar_marca(db, "MarcaTotalmenteInexistenteNoBanco") is False



def test_original_get_db_behavior():
    mock_session_instance = Mock(spec=Session)
    mock_session_instance.is_active = True

    def mock_close_side_effect():
        mock_session_instance.is_active = False
    mock_session_instance.close = Mock(side_effect=mock_close_side_effect)

    with patch('app.database.SessionLocal', return_value=mock_session_instance) as mock_session_local_constructor:
        db_yielded_from_generator = None
        for db_session in get_db():
            db_yielded_from_generator = db_session
            assert db_yielded_from_generator is mock_session_instance
            assert db_yielded_from_generator.is_active is True
            break

        mock_session_local_constructor.assert_called_once()
        assert db_yielded_from_generator is not None # Confirma se executou

        mock_session_instance.close.assert_called_once()
        assert mock_session_instance.is_active is False # Verifica se a sessão foi "fechada"