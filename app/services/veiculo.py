from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.src import veiculo as crud_veiculo
from app.schemas.veiculo import VeiculoCreate, VeiculoUpdate, Veiculo

MARCAS_VALIDAS = [
    "Chevrolet", "Ford", "Volkswagen", "Fiat", "Toyota", "Honda", "Hyundai",
    "Nissan", "Renault", "Peugeot", "Citroën", "Jeep", "Kia", "BMW",
    "Mercedes-Benz", "Audi", "Mitsubishi", "Chery", "Subaru", "Volvo"
]

def is_valid_marca(marca: str) -> bool:
    """Verifica se a marca fornecida está na lista de marcas válidas (case-insensitive)."""
    return marca.capitalize() in MARCAS_VALIDAS

class VeiculoService:
    def __init__(self, db: Session):
        self.db = db

    def criar_veiculo(self, veiculo: VeiculoCreate) -> Veiculo:
        """
        Cria um novo veículo com validações adicionais.
        """
        ano_atual = datetime.now().year
        if veiculo.ano < 1900 or veiculo.ano > ano_atual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ano inválido. Deve estar entre 1900 e {ano_atual}"
            )

        if not is_valid_marca(veiculo.marca):
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Marca inválida: {veiculo.marca}. Marcas permitidas: {', '.join(MARCAS_VALIDAS)}"
            )

        db_veiculo = crud_veiculo.create_veiculo(self.db, veiculo)
        return Veiculo.model_validate(db_veiculo)

    def obter_veiculo(self, veiculo_id: int) -> Veiculo:
        """
        Obtém um veículo específico por ID.
        """
        db_veiculo = crud_veiculo.get_veiculo(self.db, veiculo_id)
        if not db_veiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veículo não encontrado"
            )
        return Veiculo.model_validate(db_veiculo)

    def listar_veiculos(
        self,
        skip: int = 0,
        limit: int = 100,
        marca: Optional[str] = None,
        ano: Optional[int] = None,
        cor: Optional[str] = None
    ) -> List[Veiculo]:
        """
        Lista veículos com filtros opcionais.
        """
        veiculos = crud_veiculo.get_veiculos(
            self.db,
            skip=skip,
            limit=limit,
            marca=marca,
            ano=ano,
            cor=cor
        )
        return [Veiculo.model_validate(v) for v in veiculos]

    def atualizar_veiculo(
        self,
        veiculo_id: int,
        veiculo_update: VeiculoUpdate
    ) -> Veiculo:
        """
        Atualiza um veículo existente com validações.
        """
        db_veiculo = crud_veiculo.get_veiculo(self.db, veiculo_id)
        if not db_veiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veículo não encontrado"
            )

        if veiculo_update.marca is not None:
             if not is_valid_marca(veiculo_update.marca):
                 raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Marca inválida: {veiculo_update.marca}. Marcas permitidas: {', '.join(MARCAS_VALIDAS)}"
                )

        if veiculo_update.ano is not None:
            ano_atual = datetime.now().year
            if veiculo_update.ano < 1900 or veiculo_update.ano > ano_atual:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ano inválido. Deve estar entre 1900 e {ano_atual}"
                )

        db_veiculo = crud_veiculo.update_veiculo(
            self.db,
            veiculo_id,
            veiculo_update
        )
        return Veiculo.model_validate(db_veiculo)

    def remover_veiculo(self, veiculo_id: int) -> Dict[str, str]:
        """
        Remove um veículo com validações.
        """
        if not crud_veiculo.delete_veiculo(self.db, veiculo_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veículo não encontrado"
            )
        return {"message": "Veículo removido com sucesso"}

    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas gerais sobre os veículos.
        """
        return {
            "total_nao_vendidos": crud_veiculo.count_veiculos_nao_vendidos(self.db),
            "distribuicao_por_decada": crud_veiculo.get_distribuicao_por_decada(self.db),
            "distribuicao_por_fabricante": crud_veiculo.get_distribuicao_por_fabricante(self.db),
            "veiculos_ultimos_7_dias": len(crud_veiculo.get_veiculos_ultimos_7_dias(self.db))
        }

    def obter_veiculos_nao_vendidos(self) -> List[Veiculo]:
        """
        Retorna lista de veículos não vendidos.
        """
        veiculos = crud_veiculo.get_veiculos(self.db)
        nao_vendidos = [v for v in veiculos if not v.vendido]
        return [Veiculo.model_validate(v) for v in nao_vendidos]

    def obter_veiculos_recentes(self) -> List[Veiculo]:
        """
        Retorna veículos cadastrados nos últimos 7 dias.
        """
        veiculos = crud_veiculo.get_veiculos_ultimos_7_dias(self.db)
        return [Veiculo.model_validate(v) for v in veiculos]
