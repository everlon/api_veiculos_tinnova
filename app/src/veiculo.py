from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta, UTC
from typing import List, Optional, Dict, Any

from app.models.veiculo import Veiculo
from app.schemas.veiculo import VeiculoCreate, VeiculoUpdate

def create_veiculo(db: Session, veiculo: VeiculoCreate) -> Veiculo:
    """
    Cria um novo veículo no banco de dados.
    """
    db_veiculo = Veiculo(**veiculo.model_dump())
    db.add(db_veiculo)
    db.commit()
    db.refresh(db_veiculo)
    return db_veiculo

def get_veiculo(db: Session, veiculo_id: int) -> Optional[Veiculo]:
    """
    Retorna um veículo específico pelo ID.
    """
    return db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()

def get_veiculos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    marca: Optional[str] = None,
    ano: Optional[int] = None,
    cor: Optional[str] = None
) -> List[Veiculo]:
    """
    Retorna uma lista de veículos com filtros opcionais.
    """
    query = db.query(Veiculo)

    # Aplica filtros se fornecidos
    if marca:
        query = query.filter(Veiculo.marca.ilike(f"%{marca}%"))
    if ano:
        query = query.filter(Veiculo.ano == ano)
    if cor:
        query = query.filter(Veiculo.veiculo.ilike(f"%{cor}%"))

    return query.offset(skip).limit(limit).all()

def update_veiculo(
    db: Session,
    veiculo_id: int,
    veiculo_update: VeiculoUpdate
) -> Optional[Veiculo]:
    """
    Atualiza um veículo existente.
    """
    db_veiculo = get_veiculo(db, veiculo_id)
    if not db_veiculo:
        return None

    # Atualiza apenas os campos fornecidos
    update_data = veiculo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_veiculo, field, value)

    db.commit()
    db.refresh(db_veiculo)
    return db_veiculo

def delete_veiculo(db: Session, veiculo_id: int) -> bool:
    """
    Remove um veículo do banco de dados.
    Retorna True se o veículo foi encontrado e removido, False caso contrário.
    """
    db_veiculo = get_veiculo(db, veiculo_id)
    if not db_veiculo:
        return False

    db.delete(db_veiculo)
    db.commit()
    return True

def count_veiculos_nao_vendidos(db: Session) -> int:
    """
    Retorna o total de veículos não vendidos.
    """
    return db.query(func.count(Veiculo.id)).filter(Veiculo.vendido == False).scalar()

def get_distribuicao_por_decada(db: Session) -> List[Dict[str, Any]]:
    """
    Retorna a distribuição de veículos por década de fabricação.
    """
    decada_expression = (Veiculo.ano // 10) * 10

    decadas = db.query(
        decada_expression.label("decada_inicio"),
        func.count(Veiculo.id)
    ).group_by(decada_expression).order_by(decada_expression.asc()).all()

    return [
        {"decada": f"{decada}s", "quantidade": count}
        for decada, count in decadas
    ]

def get_distribuicao_por_fabricante(db: Session) -> List[Dict[str, Any]]:
    """
    Retorna a distribuição de veículos por fabricante.
    """
    fabricantes = db.query(
        Veiculo.marca,
        func.count(Veiculo.id)
    ).group_by(Veiculo.marca).all()

    return [
        {"fabricante": marca, "quantidade": count}
        for marca, count in fabricantes
    ]

def get_veiculos_ultimos_7_dias(db: Session) -> List[Veiculo]:
    """
    Retorna os veículos cadastrados nos últimos 7 dias.
    """
    data_limite = datetime.now(UTC) - timedelta(days=7)
    return db.query(Veiculo).filter(Veiculo.created >= data_limite).all()

def validar_marca(db: Session, marca: str) -> bool:
    """
    Valida se a marca existe no banco de dados.
    Retorna True se a marca existe, False caso contrário.
    """
    marca_existente = db.query(Veiculo).filter(
        Veiculo.marca.ilike(f"%{marca}%")
    ).first()
    return marca_existente is not None
