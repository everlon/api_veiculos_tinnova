from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VeiculoBase(BaseModel):
    veiculo: str
    marca: str
    ano: int = Field(..., gt=1800, lt=datetime.now().year + 2, description="Ano de fabricação do veículo")
    descricao: Optional[str] = None
    vendido: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "veiculo": "Gol",
                    "marca": "Volkswagen",
                    "ano": 2020,
                    "descricao": "Carro popular 1.0",
                    "vendido": False,
                }
            ]
        }
    }

class VeiculoCreate(VeiculoBase):
    pass # Não adicionamos campos extras para criação

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "veiculo": "Onix Plus",
                    "marca": "Chevrolet",
                    "ano": 2023,
                    "descricao": "Sedan compacto com multimidia",
                    "vendido": True,
                }
            ]
        }
    }

class VeiculoUpdate(VeiculoBase):
    # Campos que podem ser atualizados. Tornando todos opcionais
    veiculo: Optional[str] = None
    marca: Optional[str] = None
    ano: Optional[int] = Field(None, gt=1800, lt=datetime.now().year + 2, description="Ano de fabricação do veículo")
    descricao: Optional[str] = None
    vendido: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "veiculo": "HB20S",
                    "vendido": True,
                }
            ]
        }
    }

class Veiculo(VeiculoBase):
    id: int
    created: datetime
    updated: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "veiculo": "Gol",
                    "marca": "Volkswagen",
                    "ano": 2020,
                    "descricao": "Carro popular 1.0",
                    "vendido": False,
                    "created": "2023-10-27T10:00:00.123456",
                    "updated": "2023-10-27T10:00:00.123456",
                }
            ]
        },
        "from_attributes": True
    }
